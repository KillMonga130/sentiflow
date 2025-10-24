#!/bin/bash

# Deploy to Google Cloud Run

set -e

echo "🚀 Deploying SentiFlow to Google Cloud Run"
echo "==========================================="
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${DEPLOY_REGION:-us-central1}"
SERVICE_NAME="sentiflow"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Authenticate
echo -e "${BLUE}Step 1: Authenticating with Google Cloud...${NC}"
gcloud auth configure-docker
echo -e "${GREEN}✅ Authenticated${NC}"

# Step 2: Build Docker image
echo -e "${BLUE}Step 2: Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:latest .
echo -e "${GREEN}✅ Image built${NC}"

# Step 3: Push to Container Registry
echo -e "${BLUE}Step 3: Pushing to Google Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest
echo -e "${GREEN}✅ Image pushed${NC}"

# Step 4: Deploy to Cloud Run
echo -e "${BLUE}Step 4: Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID}" \
    --set-env-vars "ELASTIC_CLOUD_ID=${ELASTIC_CLOUD_ID}" \
    --set-secrets "ELASTIC_API_KEY=elastic-api-key:latest" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

echo -e "${GREEN}✅ Deployed to Cloud Run${NC}"

# Step 5: Get service URL
echo -e "${BLUE}Step 5: Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Your application is live at:"
echo -e "${BLUE}${SERVICE_URL}${NC}"
echo ""
