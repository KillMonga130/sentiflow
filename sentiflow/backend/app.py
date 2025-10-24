"""
SentiFlow Flask Application
REST API for customer sentiment intelligence platform
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from datetime import datetime
from typing import Dict, List
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.generator import ResponseGenerator
from agents.sentiment import SentimentAnalyzer
from utils.elastic_client import ElasticClient
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize components
response_generator = None
sentiment_analyzer = None
es_client = None

# Analytics storage (in-memory for demo, use database in production)
analytics_data = {
    "total_queries": 0,
    "sentiment_distribution": {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "frustrated": 0,
        "urgent": 0
    },
    "recent_queries": []
}


@app.before_request
def initialize_components():
    """Initialize AI components on first request (lazy loading)"""
    global response_generator, sentiment_analyzer, es_client
    
    if response_generator is None:
        try:
            logger.info("🚀 Initializing SentiFlow components...")
            response_generator = ResponseGenerator()
            sentiment_analyzer = SentimentAnalyzer()
            es_client = ElasticClient()
            logger.info("✅ All components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {str(e)}")
            # Don't raise - let individual endpoints handle missing components


@app.route('/')
def serve_index():
    """Serve the main chat interface"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/dashboard')
def serve_dashboard():
    """Serve the analytics dashboard"""
    return send_from_directory(app.static_folder, 'dashboard.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "response_generator": response_generator is not None,
            "sentiment_analyzer": sentiment_analyzer is not None,
            "elasticsearch": es_client is not None
        }
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    
    Request body:
    {
        "message": "User's question",
        "conversation_id": "optional-conversation-id"
    }
    
    Response:
    {
        "response": "AI response",
        "sentiment": {...},
        "context": {...},
        "timestamp": "..."
    }
    """
    try:
        # Validate request
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request"
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        logger.info(f"💬 Received chat message: '{user_message[:50]}...'")
        
        # Check if components are initialized
        if response_generator is None:
            return jsonify({
                "error": "Service initializing, please try again"
            }), 503
        
        # Generate response
        result = response_generator.generate(
            query=user_message,
            retrieve_context=True,
            k=3
        )
        
        # Update analytics
        analytics_data["total_queries"] += 1
        sentiment_label = result['sentiment']['label']
        analytics_data["sentiment_distribution"][sentiment_label] += 1
        
        # Store recent query (keep last 50)
        analytics_data["recent_queries"].append({
            "message": user_message,
            "sentiment": sentiment_label,
            "timestamp": datetime.utcnow().isoformat()
        })
        if len(analytics_data["recent_queries"]) > 50:
            analytics_data["recent_queries"].pop(0)
        
        # Build response
        response = {
            "response": result['response'],
            "sentiment": result['sentiment'],
            "context": {
                "num_documents": result['context']['num_documents'],
                "sources": [
                    {
                        "title": doc.get('title', 'Untitled'),
                        "source": doc.get('source', 'Unknown')
                    }
                    for doc in result['context']['documents']
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Response generated successfully")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/sentiment', methods=['POST'])
def analyze_sentiment():
    """
    Sentiment analysis endpoint (standalone)
    
    Request body:
    {
        "text": "Text to analyze"
    }
    
    Response:
    {
        "sentiment": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request"
            }), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({
                "error": "Text cannot be empty"
            }), 400
        
        if sentiment_analyzer is None:
            return jsonify({
                "error": "Service initializing, please try again"
            }), 503
        
        # Analyze sentiment
        sentiment_data = sentiment_analyzer.analyze(text)
        
        return jsonify({
            "sentiment": sentiment_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in sentiment endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/api/analytics/overview', methods=['GET'])
def analytics_overview():
    """
    Get analytics overview
    
    Response:
    {
        "total_queries": 123,
        "sentiment_distribution": {...},
        "avg_sentiment_score": 0.75
    }
    """
    try:
        # Calculate average sentiment score
        total = analytics_data["total_queries"]
        if total > 0:
            # Simple approximation: positive=1.0, neutral=0.5, negative/frustrated/urgent=0.0
            positive = analytics_data["sentiment_distribution"]["positive"]
            neutral = analytics_data["sentiment_distribution"]["neutral"]
            
            avg_score = ((positive * 1.0) + (neutral * 0.5)) / total
        else:
            avg_score = 0.0
        
        return jsonify({
            "total_queries": total,
            "sentiment_distribution": analytics_data["sentiment_distribution"],
            "avg_sentiment_score": round(avg_score, 2),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in analytics overview: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500


@app.route('/api/analytics/recent', methods=['GET'])
def analytics_recent():
    """
    Get recent queries
    
    Query params:
    - limit: Number of queries to return (default: 10)
    
    Response:
    {
        "queries": [...]
    }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 50)  # Cap at 50
        
        recent = analytics_data["recent_queries"][-limit:]
        recent.reverse()  # Most recent first
        
        return jsonify({
            "queries": recent,
            "count": len(recent),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in analytics recent: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history"""
    try:
        if response_generator:
            response_generator.reset_conversation()
            return jsonify({
                "message": "Conversation reset successfully"
            })
        else:
            return jsonify({
                "error": "Service not initialized"
            }), 503
            
    except Exception as e:
        logger.error(f"❌ Error resetting conversation: {str(e)}")
        return jsonify({
            "error": "Internal server error"
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    """Run the Flask application"""
    port = int(os.environ.get('PORT', 8080))
    
    logger.info(f"🚀 Starting SentiFlow on port {port}")
    logger.info(f"📍 Main interface: http://localhost:{port}/")
    logger.info(f"📊 Analytics dashboard: http://localhost:{port}/dashboard")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )
