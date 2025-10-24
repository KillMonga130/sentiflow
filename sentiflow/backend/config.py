"""
Configuration Module for SentiFlow
Loads and validates environment variables
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration class"""
    
    # Google Cloud
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
    GCP_REGION = os.getenv('GCP_REGION', 'us-central1')
    VERTEX_AI_LOCATION = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-004')
    
    # Elastic
    ELASTIC_CLOUD_ID = os.getenv('ELASTIC_CLOUD_ID')
    ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY')
    ELASTIC_INDEX_NAME = os.getenv('ELASTIC_INDEX_NAME', 'sentiflow-kb')
    
    # Application
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 8080))
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Optional: BigQuery
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'sentiflow_analytics')
    BIGQUERY_TABLE = os.getenv('BIGQUERY_TABLE', 'conversation_logs')
    
    # Optional: Pub/Sub
    PUBSUB_TOPIC = os.getenv('PUBSUB_TOPIC', 'sentiflow-events')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            'GCP_PROJECT_ID',
            'ELASTIC_CLOUD_ID',
            'ELASTIC_API_KEY'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please create a .env file based on .env.example"
            )
        
        return True


# Validate configuration on import
if __name__ != '__main__':
    try:
        Config.validate()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")
