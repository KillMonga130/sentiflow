"""
Sentiment Analysis Module
Real-time emotion detection using Google Cloud Gemini AI
"""

import vertexai
from vertexai.generative_models import GenerativeModel
import json
import logging
from typing import Dict
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes customer sentiment using Gemini AI
    Detects emotions and classifies sentiment for personalized responses
    """
    
    def __init__(self):
        """Initialize Vertex AI and Gemini model"""
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=Config.GCP_PROJECT_ID,
                location=Config.VERTEX_AI_LOCATION
            )
            
            # Initialize Gemini model - use simple name to avoid SDK path bugs
            self.model = GenerativeModel(Config.GEMINI_MODEL)
            
            logger.info(f"✅ Initialized SentimentAnalyzer with {Config.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize SentimentAnalyzer: {str(e)}")
            raise
    
    def analyze(self, message: str) -> Dict:
        """
        Analyze sentiment of a customer message
        
        Args:
            message: Customer's message text
            
        Returns:
            Dictionary with:
            - score: float (0-1, 0=very negative, 1=very positive)
            - label: str ("positive", "neutral", "negative", "frustrated", "urgent")
            - emotion: str (primary emotion detected)
            - confidence: float (0-1, model's confidence in classification)
        """
        try:
            # Build prompt for sentiment analysis
            prompt = f"""You are a sentiment analysis expert. Analyze the sentiment and emotion in this customer service message.

Customer Message: "{message}"

Analyze and return ONLY a JSON object (no markdown, no explanations) with this EXACT structure:
{{
  "score": <float between 0.0 and 1.0, where 0=very negative, 0.5=neutral, 1=very positive>,
  "label": "<one of: positive, neutral, negative, frustrated, urgent>",
  "emotion": "<primary emotion: happy, satisfied, neutral, confused, disappointed, angry, frustrated, anxious, urgent>",
  "confidence": <float between 0.0 and 1.0 indicating classification confidence>
}}

Rules:
- "frustrated" = customer is annoyed or impatient, showing irritation
- "urgent" = customer needs immediate help or expresses time pressure
- "negative" = unhappy but not yet frustrated
- "neutral" = factual inquiry without strong emotion
- "positive" = satisfied or happy tone

JSON output:"""
            
            # Generate response
            response = self.model.generate_content(
                prompt
            )
            
            # Parse JSON from response
            result = self._parse_sentiment_json(response.text)
            
            logger.debug(f"💭 Sentiment: {result['label']} (score: {result['score']:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {str(e)}")
            # Return neutral sentiment as fallback
            return self._get_fallback_sentiment()
    
    def _parse_sentiment_json(self, response_text: str) -> Dict:
        """
        Parse JSON from Gemini response
        Handles various response formats (with or without markdown)
        """
        try:
            # Clean the response
            text = response_text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                # Find the JSON content between backticks
                parts = text.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("{"):
                        text = part
                        break
            
            # Parse JSON
            result = json.loads(text)
            
            # Validate structure
            required_keys = ['score', 'label', 'emotion', 'confidence']
            if not all(key in result for key in required_keys):
                raise ValueError("Missing required keys in sentiment response")
            
            # Validate values
            result['score'] = max(0.0, min(1.0, float(result['score'])))
            result['confidence'] = max(0.0, min(1.0, float(result['confidence'])))
            
            valid_labels = ['positive', 'neutral', 'negative', 'frustrated', 'urgent']
            if result['label'] not in valid_labels:
                result['label'] = 'neutral'
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            logger.error(f"Response text: {response_text}")
            return self._get_fallback_sentiment()
        except Exception as e:
            logger.error(f"Error parsing sentiment: {str(e)}")
            return self._get_fallback_sentiment()
    
    def _get_fallback_sentiment(self) -> Dict:
        """Return neutral sentiment when analysis fails"""
        return {
            "score": 0.5,
            "label": "neutral",
            "emotion": "unknown",
            "confidence": 0.3
        }
    
    def get_tone_instruction(self, sentiment: Dict) -> str:
        """
        Get tone instruction for response generator based on sentiment
        
        Args:
            sentiment: Sentiment analysis result
            
        Returns:
            String with tone instructions
        """
        label = sentiment['label']
        
        if label == "frustrated":
            return ("The customer is frustrated or annoyed. Be extra empathetic, "
                   "apologize for any inconvenience, acknowledge their frustration, "
                   "and focus on solving their issue quickly and efficiently.")
        
        elif label == "urgent":
            return ("The customer needs urgent help or is time-sensitive. "
                   "Be concise, prioritize immediate solutions, skip unnecessary details, "
                   "and provide clear next steps quickly.")
        
        elif label == "negative":
            return ("The customer is unhappy or disappointed. Show understanding, "
                   "apologize sincerely, and work to turn their experience around. "
                   "Be solution-focused and reassuring.")
        
        elif label == "positive":
            return ("The customer has a positive tone. Match their energy, "
                   "be friendly and enthusiastic! Use a warm, conversational style.")
        
        else:  # neutral
            return ("Maintain a professional, helpful, and friendly tone. "
                   "Be clear and informative.")
    
    def is_high_priority(self, sentiment: Dict) -> bool:
        """
        Determine if message should be high priority
        
        Args:
            sentiment: Sentiment analysis result
            
        Returns:
            bool: True if high priority (frustrated or urgent)
        """
        return sentiment['label'] in ['frustrated', 'urgent']


# Test function
if __name__ == "__main__":
    """Test the sentiment analyzer"""
    analyzer = SentimentAnalyzer()
    
    # Test messages with different sentiments
    test_messages = [
        "Hi! I'd like to know about your return policy.",  # Positive
        "I have a question about shipping times.",  # Neutral
        "My order is late and I'm not happy about it.",  # Negative
        "This is ridiculous! I've been waiting for 3 days!",  # Frustrated
        "URGENT: Need help NOW! My payment failed!",  # Urgent
    ]
    
    print("🧪 Testing Sentiment Analyzer\n")
    print("=" * 60)
    
    for message in test_messages:
        print(f"\nMessage: \"{message}\"")
        sentiment = analyzer.analyze(message)
        print(f"  Label: {sentiment['label']}")
        print(f"  Score: {sentiment['score']:.2f}")
        print(f"  Emotion: {sentiment['emotion']}")
        print(f"  Confidence: {sentiment['confidence']:.2f}")
        print(f"  High Priority: {analyzer.is_high_priority(sentiment)}")
        print("-" * 60)
