"""
Response Generator Module
Uses RAG pattern to generate context-aware, sentiment-adaptive responses
"""

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import time
import sys
import os
import logging
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.retriever import HybridRetriever
from agents.sentiment import SentimentAnalyzer
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates customer support responses using RAG:
    1. Retrieve relevant context from knowledge base
    2. Analyze customer sentiment
    3. Generate response adapted to sentiment + context
    """
    
    def __init__(self):
        """Initialize Gemini model, retriever, and sentiment analyzer"""
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=Config.GCP_PROJECT_ID,
                location=Config.VERTEX_AI_LOCATION
            )
            
            # Candidate models in fallback order (first is the configured one)
            self._model_names = [
                Config.GEMINI_MODEL,
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
            ]

            # Set default generation config (kept modest to reduce quota pressure)
            self._gen_config = GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=512,
            )

            # Lazy model init; we will instantiate per-attempt to allow fallback
            self.model = None
            
            # Initialize retriever and sentiment analyzer
            self.retriever = HybridRetriever()
            self.sentiment_analyzer = SentimentAnalyzer()
            
            # Conversation history (for context)
            self.conversation_history: List[Dict] = []
            
            logger.info(f"✅ Initialized ResponseGenerator with {Config.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ResponseGenerator: {str(e)}")
            raise
    
    def format_context(self, documents: List[Dict]) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Document {i}: {doc.get('title', 'Untitled')}]\n"
                f"{doc.get('text', '')}\n"
            )
        
        return "\n".join(context_parts)
    
    def build_prompt(
        self,
        query: str,
        context: str,
        sentiment_data: Dict,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Build the complete prompt for Gemini
        
        Args:
            query: Customer's question
            context: Retrieved context from knowledge base
            sentiment_data: Sentiment analysis results
            conversation_history: Previous messages
            
        Returns:
            Complete prompt string
        """
        # Get tone instruction based on sentiment
        tone_instruction = self.sentiment_analyzer.get_tone_instruction(sentiment_data)
        
        # Build conversation history section
        history_section = ""
        if conversation_history:
            history_section = "\n## Previous Conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 exchanges
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_section += f"{role.upper()}: {content}\n"
        
        # Build complete prompt
        prompt = f"""You are a helpful customer support agent for an e-commerce company.

## Your Task:
Answer the customer's question using the provided context from the knowledge base.
{tone_instruction}

{history_section}

## Knowledge Base Context:
{context}

## Customer's Current Question:
{query}

## Instructions:
1. Use ONLY information from the knowledge base context above
2. If the context doesn't contain the answer, politely say you don't have that information
3. Be concise but thorough
4. Use a friendly, professional tone
5. Adapt your response style based on the customer's sentiment

## Your Response:
"""
        
        return prompt
    
    def generate(
        self,
        query: str,
        retrieve_context: bool = True,
        k: int = 3
    ) -> Dict:
        """
        Generate a response to the customer query
        
        Args:
            query: Customer's question
            retrieve_context: Whether to retrieve context (set False for testing)
            k: Number of documents to retrieve
            
        Returns:
            Dictionary with response, sentiment, context, and metadata
        """
        try:
            logger.info(f"💬 Generating response for: '{query[:50]}...'")
            
            # Step 1: Analyze sentiment
            sentiment_data = self.sentiment_analyzer.analyze(query)
            logger.info(
                f"😊 Sentiment: {sentiment_data['label']} "
                f"({sentiment_data['emotion']}, {sentiment_data['confidence']:.2f})"
            )
            
            # Step 2: Retrieve context
            documents = []
            context = ""
            
            if retrieve_context:
                documents = self.retriever.retrieve(query, k=k)
                context = self.format_context(documents)
                logger.info(f"📚 Retrieved {len(documents)} documents")
            else:
                context = "No context retrieval requested."
            
            # Step 3: Build prompt
            prompt = self.build_prompt(
                query=query,
                context=context,
                sentiment_data=sentiment_data,
                conversation_history=self.conversation_history
            )
            
            # Step 4: Generate response
            logger.info("🤖 Generating response with Gemini...")

            # Try primary + fallback models with basic backoff on 429s
            last_error: Optional[Exception] = None
            response_text = None
            for model_name in self._model_names:
                try:
                    # Skip duplicates while preserving order
                    if model_name is None:
                        continue
                    logger.info(f"🧠 Using model: {model_name}")
                    self.model = GenerativeModel(model_name=model_name, generation_config=self._gen_config)

                    # Up to 2 quick retries for transient quota issues
                    for attempt in range(1, 3):
                        try:
                            response = self.model.generate_content(prompt)
                            response_text = response.text
                            break
                        except Exception as e:
                            msg = str(e)
                            if "429" in msg or "Resource exhausted" in msg:
                                wait_s = 1.5 * attempt
                                logger.warning(f"⏳ Rate limited on {model_name} (attempt {attempt}); retrying in {wait_s:.1f}s...")
                                time.sleep(wait_s)
                                last_error = e
                                continue
                            else:
                                last_error = e
                                raise

                    if response_text:
                        # Successful generation
                        break

                except Exception as e:
                    last_error = e
                    logger.warning(f"⚠️ Model {model_name} failed: {e}")
                    # Try next fallback model
                    continue

            if not response_text:
                # All models failed
                raise last_error if last_error else RuntimeError("Failed to generate response with available models")
            
            # Step 5: Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            logger.info(f"✅ Response generated ({len(response_text)} chars)")
            
            # Return complete result
            return {
                "response": response_text,
                "sentiment": sentiment_data,
                "context": {
                    "documents": documents,
                    "num_documents": len(documents)
                },
                "metadata": {
                    "query": query,
                    "model": Config.GEMINI_MODEL,
                    "retrieval_enabled": retrieve_context
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {str(e)}")
            raise
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🔄 Conversation history reset")


# Test function
if __name__ == "__main__":
    """Test the response generator"""
    generator = ResponseGenerator()
    
    # Test queries with different sentiments
    test_queries = [
        "What is your return policy?",
        "I've been waiting 3 weeks for my order! This is unacceptable!",
        "Can you help me understand the warranty terms?",
        "Your product is broken and customer service is terrible!!!",
    ]
    
    print("🧪 Testing Response Generator\n")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        
        try:
            # Generate response
            result = generator.generate(query, retrieve_context=True, k=2)
            
            # Display results
            print(f"\n😊 SENTIMENT: {result['sentiment']['label'].upper()}")
            print(f"   Emotion: {result['sentiment']['emotion']}")
            print(f"   Score: {result['sentiment']['score']:.2f}")
            print(f"   Confidence: {result['sentiment']['confidence']:.2f}")
            
            print(f"\n📚 CONTEXT: {result['context']['num_documents']} documents retrieved")
            
            print(f"\n💬 RESPONSE:")
            print(f"{result['response']}")
            
            print(f"\n{'-'*80}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Reset for next test
        generator.reset_conversation()
    
    print("\n✅ Testing complete!")
