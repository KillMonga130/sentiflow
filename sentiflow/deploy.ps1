param(
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = $(if ($env:DEPLOY_REGION) { $env:DEPLOY_REGION } else { 'us-central1' }),
    [switch]$UseSecret,
    [switch]$UseSource
)

$ErrorActionPreference = 'Stop'

Write-Host "`n🚀 Deploying SentiFlow to Google Cloud Run (PowerShell)" -ForegroundColor Cyan
Write-Host "=====================================================`n"

# Load .env if present
$envPath = Join-Path $PSScriptRoot '.env'
if (Test-Path $envPath) {
    Write-Host "Loading .env file..." -ForegroundColor Yellow
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^(?!#)([^=]+)=(.*)$') {
            $name = $Matches[1].Trim()
            $value = $Matches[2].Trim()
            # Strip quotes if present
            if ($value.StartsWith('"') -and $value.EndsWith('"')) { $value = $value.Trim('"') }
            if ($value.StartsWith("'") -and $value.EndsWith("'")) { $value = $value.Trim("'") }
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# If ProjectId wasn't passed but is now available from .env, adopt it
if (-not $ProjectId -and $env:GCP_PROJECT_ID) { $ProjectId = $env:GCP_PROJECT_ID }
if (-not $ProjectId) { $ProjectId = Read-Host "Enter GCP Project ID" }
if (-not $env:ELASTIC_CLOUD_ID) { $env:ELASTIC_CLOUD_ID = Read-Host "Enter Elastic Cloud ID" }
if (-not $env:ELASTIC_API_KEY -and -not $UseSecret) { $env:ELASTIC_API_KEY = Read-Host -AsSecureString "Enter Elastic API Key" | ForEach-Object { [System.Net.NetworkCredential]::new("user", $_).Password } }

# Defaults for optional vars
if (-not $env:VERTEX_AI_LOCATION) { $env:VERTEX_AI_LOCATION = 'us-central1' }

$serviceName = 'sentiflow'
$imageName = "gcr.io/$ProjectId/$serviceName:latest"

Write-Host "Project: $ProjectId" -ForegroundColor Gray
Write-Host "Region:  $Region" -ForegroundColor Gray
Write-Host ("Image:   {0}" -f $imageName) -ForegroundColor Gray
Write-Host ""  -ForegroundColor Gray

# Ensure gcloud project is set
Write-Host "Setting gcloud project..." -ForegroundColor Yellow
& gcloud config set project $ProjectId | Out-Host

# Enable required APIs (idempotent)
Write-Host "Enabling required APIs (Vertex AI, Cloud Run, Artifact Registry)..." -ForegroundColor Yellow
& gcloud services enable aiplatform.googleapis.com run.googleapis.com artifactregistry.googleapis.com | Out-Host

if (-not $UseSource) {
    # Local Docker path
    Write-Host "Configuring Docker auth for gcloud..." -ForegroundColor Yellow
    & gcloud auth configure-docker gcr.io --quiet | Out-Host

    Write-Host "Building Docker image..." -ForegroundColor Yellow
    & docker build -t $imageName $PSScriptRoot | Out-Host

    Write-Host "Pushing image to Container Registry..." -ForegroundColor Yellow
    & docker push $imageName | Out-Host
} else {
    Write-Host "Skipping local Docker. Will build from source in Google Cloud (using Dockerfile)." -ForegroundColor Yellow

    # Determine project number and Cloud Build service account
    Write-Host "Resolving project number and Cloud Build service account..." -ForegroundColor Yellow
    $projectNumber = (& gcloud projects describe $ProjectId --format 'value(projectNumber)')
    if (-not $projectNumber) { throw "Unable to resolve project number for $ProjectId" }
    $buildSa = "$projectNumber@cloudbuild.gserviceaccount.com"
    Write-Host "Build service account: $buildSa" -ForegroundColor Gray

    # Grant required roles to Cloud Build service account (idempotent)
    Write-Host "Ensuring IAM roles for Cloud Build service account..." -ForegroundColor Yellow
    $roles = @(
        'roles/run.admin',
        'roles/iam.serviceAccountUser',
        'roles/artifactregistry.writer',
        'roles/storage.admin'
    )
    foreach ($role in $roles) {
        try {
            & gcloud projects add-iam-policy-binding $ProjectId `
                --member "serviceAccount:$buildSa" `
                --role $role | Out-Null
        } catch {
            # Ignore if already bound or if permission denied (user may lack owner); will fail later if truly required
        }
    }

    # Stash for later deploy args
    $env:CLOUDBUILD_SA = $buildSa
}

# Optional: manage secret
if ($UseSecret) {
    Write-Host "Using Secret Manager for ELASTIC_API_KEY..." -ForegroundColor Yellow
    if (-not $env:ELASTIC_API_KEY) {
        $plain = Read-Host -AsSecureString "Enter Elastic API Key" | ForEach-Object { [System.Net.NetworkCredential]::new("user", $_).Password }
    } else {
        $plain = $env:ELASTIC_API_KEY
    }

    # Ensure Secret Manager API
    & gcloud services enable secretmanager.googleapis.com | Out-Host

    $secretName = 'elastic-api-key'
    $exists = $false
    try {
        & gcloud secrets describe $secretName --project $ProjectId --format='get(name)' | Out-Null
        $exists = $true
    } catch {
        $exists = $false
    }

    if ($exists) {
        Write-Host "Adding new secret version for '$secretName'..." -ForegroundColor Yellow
        $tmp = New-TemporaryFile
        Set-Content -Path $tmp -Value $plain -NoNewline
        & gcloud secrets versions add $secretName --project $ProjectId --data-file $tmp.FullName | Out-Host
        Remove-Item $tmp -Force
    } else {
        Write-Host "Creating secret '$secretName'..." -ForegroundColor Yellow
        $tmp = New-TemporaryFile
        Set-Content -Path $tmp -Value $plain -NoNewline
        & gcloud secrets create $secretName --project $ProjectId --data-file $tmp.FullName | Out-Host
        Remove-Item $tmp -Force
    }
}

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow

if (-not $UseSource) {
    $commonArgs = @(
        'run','deploy',$serviceName,
        '--image', $imageName,
        '--platform','managed',
        '--region', $Region,
        '--allow-unauthenticated',
        '--memory','2Gi',
        '--cpu','2',
        '--timeout','300',
        '--max-instances','10',
        '--min-instances','0'
    )
} else {
    $commonArgs = @(
        'run','deploy',$serviceName,
        '--source', $PSScriptRoot,
        '--platform','managed',
        '--region', $Region,
        '--allow-unauthenticated',
        '--memory','2Gi',
        '--cpu','2',
        '--timeout','300',
        '--max-instances','10',
        '--min-instances','0'
    )
    # Cloud Build will use default service account (already has required roles)
}

if ($UseSecret) {
    $deployArgs = $commonArgs + @(
        '--set-env-vars', "GCP_PROJECT_ID=$ProjectId",
        '--set-env-vars', "ELASTIC_CLOUD_ID=$($env:ELASTIC_CLOUD_ID)",
        '--set-secrets', 'ELASTIC_API_KEY=elastic-api-key:latest'
    )
} else {
    $deployArgs = $commonArgs + @(
        '--set-env-vars', "GCP_PROJECT_ID=$ProjectId",
        '--set-env-vars', "ELASTIC_CLOUD_ID=$($env:ELASTIC_CLOUD_ID)",
        '--set-env-vars', "ELASTIC_API_KEY=$($env:ELASTIC_API_KEY)"
    )
}

# Add optional env vars if present
if ($env:VERTEX_AI_LOCATION) {
    $deployArgs += @('--set-env-vars', "VERTEX_AI_LOCATION=$($env:VERTEX_AI_LOCATION)")
}
if ($env:GEMINI_MODEL) {
    $deployArgs += @('--set-env-vars', "GEMINI_MODEL=$($env:GEMINI_MODEL)")
}
if ($env:EMBEDDING_MODEL) {
    $deployArgs += @('--set-env-vars', "EMBEDDING_MODEL=$($env:EMBEDDING_MODEL)")
}
if ($env:ELASTIC_INDEX_NAME) {
    $deployArgs += @('--set-env-vars', "ELASTIC_INDEX_NAME=$($env:ELASTIC_INDEX_NAME)")
}

& gcloud @deployArgs | Out-Host

# Fetch URL
Write-Host "Fetching service URL..." -ForegroundColor Yellow
$serviceUrl = (& gcloud run services describe $serviceName --platform managed --region $Region --format 'value(status.url)')

Write-Host "`n=====================================================" -ForegroundColor Green
Write-Host "🎉 Deployment complete!" -ForegroundColor Green
Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
Write-Host "=====================================================`n" -ForegroundColor Green
