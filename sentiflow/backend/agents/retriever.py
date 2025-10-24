"""
Hybrid Search Retriever Module
Combines semantic (vector) and keyword search for optimal retrieval
"""

import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
import sys
import os
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.elastic_client import ElasticClient
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Retrieves relevant documents using hybrid search:
    - Semantic search (vector similarity)
    - Keyword search (BM25)
    - RRF (Reciprocal Rank Fusion) for combining results
    """
    
    def __init__(self):
        """Initialize Vertex AI embedding model and Elasticsearch client"""
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=Config.GCP_PROJECT_ID,
                location=Config.VERTEX_AI_LOCATION
            )
            
            # Initialize embedding model
            self.embedding_model = TextEmbeddingModel.from_pretrained(
                Config.EMBEDDING_MODEL
            )
            
            # Initialize Elasticsearch client
            self.es_client = ElasticClient()
            
            logger.info(f"✅ Initialized HybridRetriever")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize HybridRetriever: {str(e)}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        try:
            # Use RETRIEVAL_QUERY task type for queries
            inputs = [TextEmbeddingInput(text=query, task_type="RETRIEVAL_QUERY")]
            embeddings = self.embedding_model.get_embeddings(inputs)
            
            return embeddings[0].values
            
        except Exception as e:
            logger.error(f"❌ Error generating query embedding: {str(e)}")
            raise
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[Dict]:
        """
        Retrieve relevant documents using hybrid search
        
        Args:
            query: User's search query
            k: Number of documents to retrieve
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            
        Returns:
            List of documents with scores and snippets
        """
        try:
            logger.info(f"🔍 Retrieving top {k} documents for: '{query[:50]}...'")
            
            # Generate query embedding
            query_embedding = self.generate_query_embedding(query)
            
            # Perform hybrid search
            results = self.es_client.hybrid_search(
                query_text=query,
                query_embedding=query_embedding,
                k=k,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight
            )
            
            # Log results
            if results:
                logger.info(f"✅ Retrieved {len(results)} documents")
                for i, doc in enumerate(results[:3], 1):
                    logger.debug(f"  {i}. {doc.get('title', 'Untitled')} (score: {doc['score']:.2f})")
            else:
                logger.warning("⚠️  No documents found")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error retrieving documents: {str(e)}")
            raise
    
    def retrieve_with_filter(
        self,
        query: str,
        category: str = None,
        k: int = 5
    ) -> List[Dict]:
        """
        Retrieve documents with category filtering
        
        Args:
            query: Search query
            category: Filter by document category
            k: Number of results
            
        Returns:
            List of filtered documents
        """
        # For now, retrieve all and filter in memory
        # In production, add filter to Elasticsearch query
        results = self.retrieve(query, k=k*2)  # Get more to account for filtering
        
        if category:
            results = [doc for doc in results if doc.get('category') == category]
            results = results[:k]
        
        return results


# Test function
if __name__ == "__main__":
    """Test the hybrid retriever"""
    retriever = HybridRetriever()
    
    # Test queries
    test_queries = [
        "return policy",
        "how long does shipping take",
        "warranty information",
    ]
    
    print("🧪 Testing Hybrid Retriever\n")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        results = retriever.retrieve(query, k=3)
        
        if results:
            for i, doc in enumerate(results, 1):
                print(f"\n{i}. {doc.get('title', 'Untitled')}")
                print(f"   Score: {doc['score']:.2f}")
                print(f"   Source: {doc.get('source', 'Unknown')}")
                print(f"   Snippet: {doc.get('snippet', '')[:100]}...")
        else:
            print("  No results found")
        
        print("-" * 60)
