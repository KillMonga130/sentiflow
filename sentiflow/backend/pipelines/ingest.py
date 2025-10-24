"""
Document Ingestion Pipeline
Processes documents, generates embeddings, and indexes them in Elasticsearch
"""

import vertexai
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.elastic_client import ElasticClient
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentIngestor:
    """
    Handles document ingestion pipeline:
    1. Load documents from files
    2. Chunk text into manageable pieces
    3. Generate embeddings using Vertex AI
    4. Index in Elasticsearch
    """
    
    def __init__(self):
        """Initialize Vertex AI and Elasticsearch clients"""
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
            
            logger.info(f"✅ Initialized DocumentIngestor with {Config.EMBEDDING_MODEL}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize DocumentIngestor: {str(e)}")
            raise
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Number of words per chunk
            overlap: Number of words to overlap between chunks
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
        
        logger.debug(f"📄 Split text into {len(chunks)} chunks")
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector using Vertex AI
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (embedding vector, 768 dimensions)
        """
        try:
            # Create embedding input
            inputs = [TextEmbeddingInput(text=text, task_type="RETRIEVAL_DOCUMENT")]
            
            # Generate embeddings
            embeddings = self.embedding_model.get_embeddings(inputs)
            
            # Extract values
            embedding_values = embeddings[0].values
            
            logger.debug(f"🔢 Generated embedding with {len(embedding_values)} dimensions")
            
            return embedding_values
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Create inputs
            inputs = [
                TextEmbeddingInput(text=text, task_type="RETRIEVAL_DOCUMENT")
                for text in texts
            ]
            
            # Generate embeddings (API handles batching)
            embeddings = self.embedding_model.get_embeddings(inputs)
            
            # Extract values
            embedding_values = [emb.values for emb in embeddings]
            
            logger.info(f"🔢 Generated {len(embedding_values)} embeddings")
            
            return embedding_values
            
        except Exception as e:
            logger.error(f"❌ Error generating batch embeddings: {str(e)}")
            raise
    
    def ingest_document(
        self,
        file_path: str,
        category: str = "general"
    ) -> int:
        """
        Ingest a single document file
        
        Args:
            file_path: Path to document file
            category: Document category
            
        Returns:
            Number of chunks indexed
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"📖 Reading: {file_path}")
            
            # Chunk text
            chunks = self.chunk_text(content)
            
            if not chunks:
                logger.warning(f"⚠️  No chunks created for {file_path}")
                return 0
            
            # Generate embeddings for all chunks (batch)
            chunk_texts = chunks
            embeddings = self.generate_embeddings_batch(chunk_texts)
            
            # Prepare documents for indexing
            documents = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc = {
                    "text": chunk,
                    "embedding": embedding,
                    "source": Path(file_path).name,
                    "category": category,
                    "timestamp": datetime.utcnow().isoformat(),
                    "title": f"{Path(file_path).stem} - Part {i+1}",
                    "chunk_index": i
                }
                documents.append(doc)
            
            # Bulk index documents
            success, failed = self.es_client.bulk_index_documents(documents)
            
            logger.info(f"✅ Indexed {success} chunks from {Path(file_path).name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error ingesting document {file_path}: {str(e)}")
            raise
    
    def ingest_folder(
        self,
        folder_path: str,
        category: str = "general",
        file_pattern: str = "*.txt"
    ) -> Dict:
        """
        Ingest all documents from a folder
        
        Args:
            folder_path: Path to folder containing documents
            category: Category for all documents
            file_pattern: File pattern to match (e.g., "*.txt", "*.md")
            
        Returns:
            Dictionary with ingestion statistics
        """
        try:
            folder = Path(folder_path)
            
            if not folder.exists():
                raise FileNotFoundError(f"Folder not found: {folder_path}")
            
            # Find matching files
            files = list(folder.glob(file_pattern))
            
            if not files:
                logger.warning(f"⚠️  No files matching '{file_pattern}' in {folder_path}")
                return {"total_files": 0, "total_chunks": 0, "failed_files": 0}
            
            logger.info(f"📁 Found {len(files)} files to ingest")
            
            # Ingest each file
            total_chunks = 0
            failed_files = 0
            
            for file_path in files:
                try:
                    chunks = self.ingest_document(str(file_path), category)
                    total_chunks += chunks
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path.name}: {str(e)}")
                    failed_files += 1
            
            # Summary
            stats = {
                "total_files": len(files),
                "successful_files": len(files) - failed_files,
                "failed_files": failed_files,
                "total_chunks": total_chunks
            }
            
            logger.info("=" * 60)
            logger.info("📊 Ingestion Summary:")
            logger.info(f"  Total files: {stats['total_files']}")
            logger.info(f"  Successful: {stats['successful_files']}")
            logger.info(f"  Failed: {stats['failed_files']}")
            logger.info(f"  Total chunks indexed: {stats['total_chunks']}")
            logger.info("=" * 60)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error ingesting folder: {str(e)}")
            raise


# Main execution
if __name__ == "__main__":
    """
    Run document ingestion from command line
    
    Usage:
        python ingest.py <folder_path> [category]
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest documents into SentiFlow')
    parser.add_argument(
        'folder',
        nargs='?',
        default='../../data/sample_docs',
        help='Path to folder containing documents'
    )
    parser.add_argument(
        '--category',
        default='knowledge_base',
        help='Category for documents'
    )
    parser.add_argument(
        '--pattern',
        default='*.txt',
        help='File pattern to match (default: *.txt)'
    )
    
    args = parser.parse_args()
    
    # Create ingestor
    ingestor = DocumentIngestor()
    
    # Ingest documents
    try:
        stats = ingestor.ingest_folder(
            args.folder,
            category=args.category,
            file_pattern=args.pattern
        )
        
        if stats['total_chunks'] > 0:
            logger.info("✅ Ingestion complete!")
        else:
            logger.warning("⚠️  No documents were ingested")
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {str(e)}")
        sys.exit(1)
