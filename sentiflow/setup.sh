#!/bin/bash

# SentiFlow Setup Script
# This script sets up the complete SentiFlow environment

set -e  # Exit on error

echo "🚀 SentiFlow Setup Script"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Step 2: Create virtual environment
echo -e "${BLUE}Step 2: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Step 3: Activate virtual environment
echo -e "${BLUE}Step 3: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Step 4: Install dependencies
echo -e "${BLUE}Step 4: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r backend/requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 5: Setup environment variables
echo -e "${BLUE}Step 5: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  .env file created from template${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env with your actual credentials${NC}"
    echo ""
    echo -e "${YELLOW}Required credentials:${NC}"
    echo "  - GCP_PROJECT_ID"
    echo "  - ELASTIC_CLOUD_ID"
    echo "  - ELASTIC_API_KEY"
    echo ""
    read -p "Press Enter to continue after editing .env..."
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Step 6: Setup Elasticsearch index
echo -e "${BLUE}Step 6: Setting up Elasticsearch index...${NC}"
python backend/pipelines/setup_elastic.py
echo -e "${GREEN}✅ Elasticsearch index created${NC}"

# Step 7: Ingest sample documents
echo -e "${BLUE}Step 7: Ingesting sample documents...${NC}"
python backend/pipelines/ingest.py data/sample_docs --category knowledge_base
echo -e "${GREEN}✅ Sample documents ingested${NC}"

# Step 8: Test the setup
echo -e "${BLUE}Step 8: Running tests...${NC}"
echo "Testing sentiment analyzer..."
python -c "from backend.agents.sentiment import SentimentAnalyzer; s = SentimentAnalyzer(); print('✅ Sentiment analyzer OK')"

echo "Testing retriever..."
python -c "from backend.agents.retriever import HybridRetriever; r = HybridRetriever(); print('✅ Retriever OK')"

echo -e "${GREEN}✅ All tests passed${NC}"

# Final message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 SentiFlow setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "To start the application:"
echo -e "  ${BLUE}python backend/app.py${NC}"
echo ""
echo "Then open in your browser:"
echo -e "  ${BLUE}http://localhost:8080${NC}"
echo ""
echo "Or to build and run with Docker:"
echo -e "  ${BLUE}docker build -t sentiflow .${NC}"
echo -e "  ${BLUE}docker run -p 8080:8080 --env-file .env sentiflow${NC}"
echo ""
