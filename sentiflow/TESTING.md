# 🧪 SentiFlow Testing Guide

Quick reference for testing all components before hackathon submission.

## ⚡ Quick Test Commands

### 1. Test Configuration
```bash
python backend/config.py
```
**Expected**: All config values displayed, no errors

### 2. Test Sentiment Analyzer
```bash
cd backend
python agents/sentiment.py
```
**Expected**: 5 test cases with sentiment analysis results

### 3. Test Elasticsearch Client
```bash
cd backend
python utils/elastic_client.py
```
**Expected**: Index creation and hybrid search demo

### 4. Test Retriever
```bash
cd backend
python agents/retriever.py
```
**Expected**: Retrieval results for 3 test queries

### 5. Test Response Generator
```bash
cd backend
python agents/generator.py
```
**Expected**: Full RAG responses for 4 test queries

### 6. Test API Endpoints
```bash
# Start server
python backend/app.py

# In another terminal:
# Health check
curl http://localhost:8080/api/health

# Chat
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your return policy?"}'

# Sentiment
curl -X POST http://localhost:8080/api/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product!"}'

# Analytics
curl http://localhost:8080/api/analytics/overview
curl http://localhost:8080/api/analytics/recent?limit=5
```

## 🎯 Test Scenarios

### Positive Sentiment Test
```json
{"message": "Your service is excellent! Thank you!"}
```
**Expected Sentiment**: positive, emotion: "Delighted" or "Happy"

### Neutral Sentiment Test
```json
{"message": "What are your business hours?"}
```
**Expected Sentiment**: neutral, emotion: "Calm" or "Inquisitive"

### Negative Sentiment Test
```json
{"message": "This is disappointing. Not what I expected."}
```
**Expected Sentiment**: negative, emotion: "Disappointed"

### Frustrated Sentiment Test
```json
{"message": "I've called 5 times and no one helps! This is ridiculous!"}
```
**Expected Sentiment**: frustrated, emotion: "Angry" or "Irritated"

### Urgent Sentiment Test
```json
{"message": "URGENT: Need immediate assistance with my order!"}
```
**Expected Sentiment**: urgent, emotion: "Anxious" or "Concerned"

## 🔍 Feature Verification Checklist

### Backend
- [ ] Config loads from .env correctly
- [ ] Elasticsearch connection works
- [ ] Sentiment analysis returns valid JSON
- [ ] Retriever finds relevant documents
- [ ] Generator produces coherent responses
- [ ] Flask app starts without errors
- [ ] All API endpoints respond correctly

### Frontend
- [ ] Chat interface loads
- [ ] Messages send and receive
- [ ] Sentiment indicator updates
- [ ] Loading spinner shows during processing
- [ ] Dashboard displays charts
- [ ] Analytics data updates
- [ ] Navigation between pages works

### Integration
- [ ] User message → sentiment analysis works
- [ ] Query → retrieval → response pipeline flows
- [ ] Conversation history maintained
- [ ] Analytics data accumulates
- [ ] Reset conversation clears history

### Deployment
- [ ] Docker image builds successfully
- [ ] Container runs locally
- [ ] Environment variables load correctly
- [ ] Health check endpoint accessible
- [ ] Application accessible at http://localhost:8080

## 📊 Performance Benchmarks

### Expected Response Times
- Sentiment analysis: < 1 second
- Document retrieval: < 500ms
- Full RAG response: 2-4 seconds
- Health check: < 100ms
- Analytics queries: < 200ms

### Expected Accuracy
- Sentiment classification: High confidence (>0.7) for clear emotions
- Document retrieval: Top 3 results should be relevant
- Response relevance: Should cite knowledge base accurately

## 🐛 Common Issues & Solutions

### Issue: Import errors (vertexai, elasticsearch)
**Solution**: 
```bash
pip install -r backend/requirements.txt
```

### Issue: "Service initializing" error
**Solution**: Wait 30-60 seconds for lazy loading to complete

### Issue: No documents retrieved
**Solution**: 
```bash
# Reingest documents
python backend/pipelines/ingest.py data/sample_docs
```

### Issue: Elasticsearch connection failed
**Solution**: 
- Check ELASTIC_CLOUD_ID in .env
- Verify ELASTIC_API_KEY is correct
- Confirm Elastic deployment is running

### Issue: Sentiment analysis fails
**Solution**:
- Check GCP_PROJECT_ID in .env
- Verify Vertex AI API is enabled
- Ensure proper GCP authentication

## 🎬 Demo Flow for Judges

### 1. Start Application
```bash
python backend/app.py
```

### 2. Open Chat Interface
Navigate to: http://localhost:8080

### 3. Demo Positive Interaction
**Type**: "I love your products! How do I track my order?"  
**Show**: Positive sentiment (😊), shipping info response

### 4. Demo Frustrated Customer
**Type**: "This is unacceptable! I've been waiting 3 weeks!"  
**Show**: Frustrated sentiment (😠), empathetic response

### 5. Show Analytics
Navigate to: http://localhost:8080/dashboard  
**Show**: 
- Total queries count
- Sentiment distribution chart
- Recent queries list

### 6. Demo Context Awareness
**Type**: "What about returns?"  
**Show**: Return policy information

### 7. Highlight Features
- Real-time sentiment updates
- Source attribution in responses
- Beautiful UI with animations
- Live analytics

## 📝 Pre-Submission Checklist

### Code Quality
- [ ] No commented-out code
- [ ] All imports used
- [ ] No hardcoded credentials
- [ ] Proper error handling
- [ ] Logging configured

### Documentation
- [ ] README.md complete
- [ ] DEPLOYMENT.md reviewed
- [ ] Code comments added
- [ ] API endpoints documented

### Testing
- [ ] All test files run successfully
- [ ] API endpoints tested
- [ ] Frontend loads correctly
- [ ] Analytics work
- [ ] Docker build successful

### Deployment
- [ ] .env.example up to date
- [ ] requirements.txt complete
- [ ] Dockerfile optimized
- [ ] deploy.sh tested
- [ ] .gitignore configured

### Security
- [ ] No API keys in code
- [ ] .env in .gitignore
- [ ] Secrets use environment variables
- [ ] CORS configured properly

## 🏆 Final Validation

### Run Full System Test
```bash
# 1. Setup
./setup.sh

# 2. Start server
python backend/app.py

# 3. Test all endpoints (in another terminal)
curl http://localhost:8080/api/health
curl -X POST http://localhost:8080/api/chat -H "Content-Type: application/json" -d '{"message": "test"}'

# 4. Open browser
# Visit http://localhost:8080
# Visit http://localhost:8080/dashboard

# 5. Send test messages
# 6. Verify analytics update
# 7. Reset conversation
```

### If All Tests Pass ✅
**You're ready to submit!**

### If Any Tests Fail ❌
1. Check error logs
2. Verify environment variables
3. Confirm service status
4. Retry failed component
5. Check this guide for solutions

---

**Remember**: The judges will test:
- ✅ Functionality (does it work?)
- ✅ Innovation (is it unique?)
- ✅ Code quality (is it well-written?)
- ✅ Documentation (can they understand it?)
- ✅ Production-readiness (can it deploy?)

**SentiFlow delivers on all fronts! Good luck! 🚀**
