"""
Elasticsearch Client Module
Handles all Elasticsearch operations including index creation and hybrid search
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import logging
from typing import List, Dict, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticClient:
    """
    Elasticsearch client for SentiFlow
    Manages index creation and hybrid search operations
    """
    
    def __init__(self):
        """Initialize Elasticsearch connection"""
        try:
            self.es = Elasticsearch(
                cloud_id=Config.ELASTIC_CLOUD_ID,
                api_key=Config.ELASTIC_API_KEY,
                request_timeout=30
            )
            
            # Test connection
            if self.es.ping():
                logger.info("✅ Successfully connected to Elasticsearch")
            else:
                raise ConnectionError("Failed to ping Elasticsearch")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Elasticsearch: {str(e)}")
            raise
        
        self.index_name = Config.ELASTIC_INDEX_NAME
    
    def create_index(self, delete_if_exists: bool = False) -> bool:
        """
        Create Elasticsearch index with proper mapping for hybrid search
        
        Args:
            delete_if_exists: If True, delete existing index before creating
            
        Returns:
            bool: True if successful
        """
        try:
            # Delete existing index if requested
            if delete_if_exists and self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                logger.info(f"🗑️  Deleted existing index: {self.index_name}")
            
            # Check if index already exists
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"ℹ️  Index already exists: {self.index_name}")
                return True
            
            # Define index mapping
            mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index": {
                        "max_result_window": 10000
                    }
                },
                "mappings": {
                    "properties": {
                        "text": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 768,  # text-embedding-004 dimension
                            "index": True,
                            "similarity": "cosine"
                        },
                        "source": {
                            "type": "keyword"
                        },
                        "category": {
                            "type": "keyword"
                        },
                        "timestamp": {
                            "type": "date"
                        },
                        "title": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "chunk_index": {
                            "type": "integer"
                        }
                    }
                }
            }
            
            # Create index
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Created index: {self.index_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating index: {str(e)}")
            raise
    
    def index_document(self, document: Dict) -> str:
        """
        Index a single document
        
        Args:
            document: Document dictionary with text, embedding, and metadata
            
        Returns:
            str: Document ID
        """
        try:
            response = self.es.index(
                index=self.index_name,
                document=document,
                refresh=True  # Make immediately searchable
            )
            
            doc_id = response['_id']
            logger.debug(f"📝 Indexed document: {doc_id}")
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Error indexing document: {str(e)}")
            raise
    
    def bulk_index_documents(self, documents: List[Dict]) -> tuple:
        """
        Bulk index multiple documents
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            tuple: (success_count, failed_count)
        """
        try:
            # Prepare bulk actions
            actions = [
                {
                    "_index": self.index_name,
                    "_source": doc
                }
                for doc in documents
            ]
            
            # Perform bulk indexing
            success, failed = bulk(self.es, actions, raise_on_error=False)
            
            logger.info(f"📦 Bulk indexed: {success} successful, {len(failed)} failed")
            
            # Refresh index to make documents searchable
            self.es.indices.refresh(index=self.index_name)
            
            return success, len(failed)
            
        except Exception as e:
            logger.error(f"❌ Error in bulk indexing: {str(e)}")
            raise
    
    def hybrid_search(
        self,
        query_text: str,
        query_embedding: List[float],
        k: int = 5,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword search
        
        Args:
            query_text: Text query for keyword search
            query_embedding: Vector embedding for semantic search
            k: Number of results to return
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            
        Returns:
            List of document dictionaries with scores
        """
        try:
            # Build hybrid search query
            # Using script_score for vector similarity combined with text matching
            search_body = {
                "size": k,
                "query": {
                    "bool": {
                        "should": [
                            # Semantic search component (vector similarity)
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": f"{semantic_weight} * (cosineSimilarity(params.query_vector, 'embedding') + 1.0)",
                                        "params": {
                                            "query_vector": query_embedding
                                        }
                                    }
                                }
                            },
                            # Keyword search component (BM25)
                            {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": ["text^2", "title"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                    "boost": keyword_weight
                                }
                            }
                        ]
                    }
                },
                "_source": {
                    "excludes": ["embedding"]  # Don't return large embeddings
                },
                "highlight": {
                    "fields": {
                        "text": {
                            "fragment_size": 200,
                            "number_of_fragments": 2
                        }
                    }
                }
            }
            
            # Execute search
            response = self.es.search(index=self.index_name, body=search_body)
            
            # Process results
            results = []
            for hit in response['hits']['hits']:
                doc = hit['_source']
                doc['_id'] = hit['_id']
                doc['score'] = hit['_score']
                
                # Add highlighted snippets if available
                if 'highlight' in hit and 'text' in hit['highlight']:
                    doc['snippet'] = ' ... '.join(hit['highlight']['text'])
                else:
                    # Fallback to first 200 characters
                    doc['snippet'] = doc.get('text', '')[:200] + '...'
                
                results.append(doc)
            
            logger.info(f"🔍 Hybrid search found {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in hybrid search: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """Get total number of documents in index"""
        try:
            count = self.es.count(index=self.index_name)
            return count['count']
        except Exception as e:
            logger.error(f"❌ Error getting document count: {str(e)}")
            return 0
    
    def delete_index(self) -> bool:
        """Delete the index"""
        try:
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                logger.info(f"🗑️  Deleted index: {self.index_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting index: {str(e)}")
            return False


if __name__ == "__main__":
    """Test the Elastic client"""
    client = ElasticClient()
    
    # Create index
    client.create_index(delete_if_exists=True)
    
    # Test document
    test_doc = {
        "text": "This is a test document for SentiFlow",
        "embedding": [0.1] * 768,  # Dummy embedding
        "source": "test.txt",
        "category": "test",
        "timestamp": "2025-10-24T00:00:00Z",
        "title": "Test Document"
    }
    
    # Index document
    doc_id = client.index_document(test_doc)
    print(f"Indexed document ID: {doc_id}")
    
    # Get count
    count = client.get_document_count()
    print(f"Total documents: {count}")
