# 🎥 SentiFlow Demo Script

**For AI Accelerate Hackathon 2025 - Elastic Challenge**

---

## 📹 Video Demo Structure (3-5 minutes)

### Opening (30 seconds)
**[Screen: Title Slide]**

> "Hi! I'm presenting SentiFlow - a Real-Time Customer Sentiment Intelligence Platform built for the Elastic Challenge."
>
> "SentiFlow transforms customer support by analyzing sentiment in real-time and adapting responses using Google Cloud Vertex AI and Elasticsearch."

**[Show: Architecture diagram from README.md]**

> "The system combines Google's Gemini 2.0 Flash for AI, text-embedding-004 for vectors, and Elasticsearch hybrid search to deliver context-aware, sentiment-adaptive responses."

---

### Problem Statement (30 seconds)
**[Screen: Problem slide or notes]**

> "Traditional customer support systems treat all customers the same. But a frustrated customer needs empathy, while a satisfied customer just needs quick information."
>
> "SentiFlow solves this by detecting emotional state in real-time and adapting both search and response generation accordingly."

---

### Technology Stack (30 seconds)
**[Screen: README.md - Tech Stack Table]**

> "Here's what powers SentiFlow:"
> - "Google Gemini 2.0 Flash - the latest LLM for response generation"
> - "Vertex AI text-embedding-004 - for 768-dimensional vector embeddings"
> - "Elasticsearch 8.11+ - hybrid search combining vector similarity with BM25 keyword matching"
> - "Flask backend with Cloud Run deployment for production scale"

---

### Live Demo Part 1: Positive Customer (1 minute)
**[Screen: http://localhost:8080]**

> "Let me show you SentiFlow in action."

**[Type in chat]**: "I love your products! What's your return policy?"

**[Point out]**:
> "Notice the sentiment indicator immediately shows 'Positive' with a happy emoji and high confidence score."

**[Wait for response]**

> "The AI retrieves relevant return policy information and responds in a friendly, upbeat tone matching the customer's mood."

**[Highlight]**:
- Sentiment badge (green, 😊)
- Confidence percentage
- Source attribution below response

---

### Live Demo Part 2: Frustrated Customer (1 minute)
**[Type in chat]**: "This is ridiculous! I've been waiting 3 WEEKS for my order!"

**[Point out]**:
> "Watch the sentiment indicator change to 'Frustrated' in real-time."

**[Wait for response]**

> "Notice how the response tone completely changes - it's empathetic, acknowledges the frustration, and prioritizes resolution."

**[Highlight]**:
- Sentiment badge (red, 😠)
- Tone adaptation in response
- Different knowledge base sources cited

---

### Live Demo Part 3: Analytics Dashboard (45 seconds)
**[Navigate to http://localhost:8080/dashboard]**

> "The analytics dashboard provides real-time insights."

**[Show]**:
1. **Metrics cards**:
   > "Total queries, average sentiment score, and positive rate"

2. **Sentiment distribution chart**:
   > "Visual breakdown of all sentiment categories"

3. **Trend chart**:
   > "Sentiment trends over the last 10 queries"

4. **Recent queries list**:
   > "Live feed of customer interactions with sentiment labels"

**[Click refresh button]**:
> "Data updates automatically every 10 seconds"

---

### Technical Deep Dive (45 seconds)
**[Screen: Code editor - show key files]**

> "Under the hood, here's what makes it work:"

**[Show agents/sentiment.py]**:
> "Gemini analyzes text and returns 5 sentiment categories: positive, neutral, negative, frustrated, and urgent - with emotion labels and confidence scores."

**[Show utils/elastic_client.py - hybrid_search method]**:
> "Our hybrid search combines semantic vector search using cosine similarity with BM25 keyword matching, then fuses results using Reciprocal Rank Fusion."

**[Show agents/generator.py - build_prompt method]**:
> "The RAG pipeline retrieves context, adapts tone based on sentiment, and maintains conversation memory for natural dialogue."

---

### Production Readiness (30 seconds)
**[Screen: Show Dockerfile and deploy.sh]**

> "SentiFlow is production-ready:"
> - "Multi-stage Docker builds for optimization"
> - "One-command deployment to Google Cloud Run"
> - "Comprehensive error handling and logging"
> - "Health checks and monitoring endpoints"
> - "Auto-scaling from 0 to 10 instances"

**[Show DEPLOYMENT.md]**:
> "Complete deployment guide included with step-by-step instructions."

---

### Innovation Highlights (30 seconds)
**[Screen: Summary slide]**

> "What makes SentiFlow unique:"
> 1. "Uses the latest Gemini 2.0 Flash model - just released"
> 2. "True hybrid search - best of both vector and keyword approaches"
> 3. "Real-time sentiment adaptation - not just detection"
> 4. "Production-grade architecture - ready to scale"
> 5. "Complete end-to-end solution - backend, frontend, analytics, deployment"

---

### Closing (30 seconds)
**[Screen: Back to chat interface]**

> "SentiFlow demonstrates the power of combining Google Cloud Vertex AI with Elasticsearch to create intelligent, empathetic customer experiences."

**[Show PROJECT_SUMMARY.md]**:
> "The complete source code, documentation, and deployment scripts are available in the repository."

> "Thank you for watching! I'm excited to compete in the Elastic Challenge and would love to answer any questions."

---

## 📸 Screenshots to Capture

### For Submission Documentation

1. **Chat Interface - Positive**
   - Shows happy emoji sentiment
   - Friendly response visible
   - Source attribution highlighted

2. **Chat Interface - Frustrated**
   - Shows angry emoji sentiment
   - Empathetic response visible
   - Different sources shown

3. **Analytics Dashboard - Overview**
   - All three metric cards visible
   - Sentiment distribution chart showing data
   - Clean, professional layout

4. **Analytics Dashboard - Charts**
   - Trend line chart with data points
   - Recent queries list populated
   - Refresh button visible

5. **Architecture Diagram**
   - From README.md
   - Shows full system flow
   - Clear and professional

6. **Code Quality Examples**
   - Well-commented Python code
   - Type hints visible
   - Clean structure

---

## 🎤 Talking Points for Q&A

### Technical Questions

**Q: Why hybrid search instead of just vector search?**
> "Vector search is great for semantic similarity, but it can miss exact keyword matches. BM25 excels at keywords but lacks semantic understanding. By combining both with RRF, we get the best of both worlds - finding documents that are semantically similar AND contain relevant keywords."

**Q: How do you handle API rate limits?**
> "We batch embedding requests where possible, cache conversation history to reduce LLM calls, and implement proper error handling with retries. In production, we'd add Redis caching for frequently accessed documents."

**Q: Why Gemini 2.0 Flash over other models?**
> "Gemini 2.0 Flash offers the best balance of speed and quality. It's fast enough for real-time responses (under 3 seconds) while providing nuanced sentiment analysis and high-quality RAG responses."

**Q: How does sentiment adaptation actually work?**
> "The sentiment analyzer returns a label and emotion. We use this to inject tone instructions into the RAG prompt. For example, frustrated customers get empathetic language, while positive customers get enthusiastic confirmation. The LLM naturally adapts its writing style based on these instructions."

---

### Business Questions

**Q: How would this scale in production?**
> "Cloud Run auto-scales based on demand, Elasticsearch can handle millions of documents with proper sharding, and Vertex AI has enterprise-grade reliability. The architecture separates concerns - we could add caching, load balancing, and database persistence without major rewrites."

**Q: What's the ROI for companies?**
> "Faster resolution times, improved customer satisfaction from empathetic responses, and analytics to identify common pain points. The sentiment data helps prioritize urgent cases and improve training."

**Q: What industries could use this?**
> "E-commerce (our demo), SaaS support, banking customer service, healthcare patient communication, telecom support - anywhere customer sentiment impacts outcomes."

---

## 🏆 Strengths to Emphasize

1. **Latest Technology**: "Using Gemini 2.0 Flash - Google's newest model"

2. **True Hybrid Search**: "Not just vector or keyword - we fuse both intelligently"

3. **Production Quality**: "Complete with Docker, deployment scripts, monitoring, and documentation"

4. **End-to-End Solution**: "Not a prototype - a fully functional system with UI, backend, analytics, and DevOps"

5. **Innovation**: "Real-time sentiment adaptation is unique - most systems just detect, we act on it"

6. **Comprehensive Docs**: "README, DEPLOYMENT guide, TESTING guide, PROJECT_SUMMARY - judges can understand everything"

---

## ⏱️ Time Management

**3-minute version**:
- Opening: 20s
- Problem: 20s  
- Demo positive: 40s
- Demo frustrated: 40s
- Dashboard: 30s
- Technical: 20s
- Closing: 10s

**5-minute version**:
- Opening: 30s
- Problem: 30s
- Tech stack: 30s
- Demo positive: 60s
- Demo frustrated: 60s
- Dashboard: 45s
- Technical deep dive: 45s
- Production: 30s
- Innovation: 30s
- Closing: 30s

---

## 🎬 Final Checklist

Before recording:
- [ ] Application running smoothly
- [ ] Test all demo queries work
- [ ] Analytics has some data populated
- [ ] Browser window clean (close extra tabs)
- [ ] Good lighting and audio
- [ ] Screen resolution set to 1920x1080
- [ ] Disable notifications
- [ ] Rehearse script 2-3 times

During recording:
- [ ] Speak clearly and confidently
- [ ] Show, don't just tell
- [ ] Point cursor to important elements
- [ ] Pause briefly when switching screens
- [ ] Smile (they can hear it!)
- [ ] Stay within time limit

After recording:
- [ ] Watch full video
- [ ] Check audio quality
- [ ] Verify all features shown
- [ ] Add captions if needed
- [ ] Export in high quality (1080p minimum)

---

**You've got this! SentiFlow is an impressive submission. Show it with confidence! 🚀🏆**
