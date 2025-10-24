"""
Elasticsearch Index Setup Script
Run this to create the index before ingesting documents
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.elastic_client import ElasticClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_elasticsearch():
    """Setup Elasticsearch index for SentiFlow"""
    try:
        logger.info("🚀 Starting Elasticsearch setup...")
        
        # Create client
        client = ElasticClient()
        
        # Create index (will skip if already exists)
        client.create_index(delete_if_exists=False)
        
        # Verify setup
        count = client.get_document_count()
        logger.info(f"📊 Current document count: {count}")
        
        logger.info("✅ Elasticsearch setup complete!")
        logger.info(f"📝 Index name: {client.index_name}")
        logger.info("🎯 Ready to ingest documents!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        return False


def reset_elasticsearch():
    """Delete and recreate the index (WARNING: Deletes all data!)"""
    try:
        logger.warning("⚠️  RESETTING Elasticsearch index - ALL DATA WILL BE DELETED!")
        
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            logger.info("❌ Reset cancelled")
            return False
        
        client = ElasticClient()
        
        # Delete and recreate
        client.create_index(delete_if_exists=True)
        
        logger.info("✅ Index reset complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Reset failed: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Elasticsearch for SentiFlow')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Delete and recreate index (WARNING: Deletes all data!)'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_elasticsearch()
    else:
        setup_elasticsearch()
