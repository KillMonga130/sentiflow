# FinanceGPT - AI-Powered Personal Finance Assistant

## 🏆 AI Accelerate Hackathon - Elastic Challenge Submission

An intelligent, conversational AI assistant that helps users manage their personal finances through natural language interactions powered by Elastic's hybrid search and Google Cloud's Gemini AI.

## 🎯 Problem Statement

Managing personal finances involves searching through countless receipts, invoices, bank statements, and financial documents. Traditional search is rigid and keyword-based, making it hard to find relevant information naturally.

## 💡 Solution

FinanceGPT combines:
- **Elastic's Hybrid Search**: Vector embeddings + keyword search for intelligent document retrieval
- **Google Cloud Vertex AI**: Gemini for conversational AI and context understanding
- **RAG Architecture**: Retrieval-Augmented Generation for accurate, context-aware responses

## ✨ Key Features

1. **Conversational Finance Queries**: "How much did I spend on groceries last month?"
2. **Smart Document Search**: Find receipts, invoices, and statements using natural language
3. **Financial Insights**: AI-generated summaries and spending patterns
4. **Multi-modal Support**: Process PDFs, images, and text documents
5. **Secure & Private**: All data stays within your Google Cloud & Elastic infrastructure

## 🏗️ Architecture

```
User Query → Gemini (Intent Recognition) → Elastic (Hybrid Search) → Gemini (Response Generation) → User
```

1. User asks a natural language question
2. Gemini processes and understands intent
3. Query is converted to embeddings using Vertex AI
4. Elastic performs hybrid search (vector + keyword)
5. Retrieved documents are sent to Gemini
6. Gemini generates contextual response

## 🛠️ Tech Stack

### Google Cloud
- **Vertex AI**: Text embeddings and Gemini API
- **Cloud Run**: Serverless backend deployment
- **Cloud Storage**: Document storage
- **Secret Manager**: API key management

### Elastic
- **Elasticsearch**: Hybrid search engine
- **Vector Search**: Semantic similarity matching
- **Text Search**: Keyword-based retrieval
- **ELSER**: Elastic Learned Sparse EncodeR for better relevance

### Additional Technologies
- **Python**: Backend (Flask/FastAPI)
- **React**: Frontend UI
- **Docker**: Containerization

## 📁 Project Structure

```
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── elastic_client.py      # Elastic connection & search
│   ├── gemini_client.py       # Vertex AI & Gemini integration
│   ├── document_processor.py  # PDF/Image processing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   └── services/
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   ├── elastic-setup.sh
│   └── gcp-setup.sh
├── data/
│   └── sample-documents/
├── docs/
│   └── demo-script.md
├── .env.example
├── docker-compose.yml
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Google Cloud Project with billing enabled
- Elastic Cloud deployment (or local Elasticsearch)
- Python 3.9+
- Node.js 18+
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd financegpt
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
```

5. **Set up Elastic index**
```bash
cd infrastructure
bash elastic-setup.sh
```

6. **Run the application**

Backend:
```bash
cd backend
python app.py
```

Frontend:
```bash
cd frontend
npm start
```

Or use Docker Compose:
```bash
docker-compose up
```

## 🎬 Demo Video

[YouTube Link - 3 minutes demo]

## 📊 Sample Queries

- "Show me all my utility bills from last quarter"
- "How much did I spend on dining out in September?"
- "Find my car insurance documents"
- "What were my top 5 expenses last month?"
- "Summarize my subscription payments"

## 🏅 Hackathon Requirements Checklist

- ✅ Uses Google Cloud (Vertex AI, Gemini, Cloud Run, Cloud Storage)
- ✅ Uses Elastic (Hybrid Search, Vector Database)
- ✅ Conversational AI solution
- ✅ Transforms daily life activity (personal finance)
- ✅ Open source repository with license
- ✅ Demo video (under 3 minutes)
- ✅ Hosted project URL
- ✅ Modern AI/data concepts (RAG, LLMs, Vector Search)

## 🎯 Impact

### For Individuals
- Saves hours searching through financial documents
- Better financial awareness through AI insights
- Reduced stress in tax preparation and budgeting

### For Businesses
- Scalable to expense management systems
- Compliance and audit trail automation
- Employee reimbursement processing

## 🔒 Security & Privacy

- End-to-end encryption for document storage
- No third-party data sharing
- User controls their own Google Cloud & Elastic instances
- GDPR compliant design

## 📈 Future Enhancements

- [ ] Multi-language support
- [ ] Mobile app (iOS/Android)
- [ ] Bank account integration
- [ ] Predictive budgeting with ML
- [ ] Voice interface
- [ ] Automated categorization and tagging

## 👥 Team

[Your team information]

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Google Cloud for powerful AI infrastructure
- Elastic for industry-leading search technology
- Devpost for hosting this amazing hackathon

## 📞 Contact

[Your contact information]

---

Built with ❤️ for AI Accelerate Hackathon 2025
