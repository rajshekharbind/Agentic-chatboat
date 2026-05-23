# 🤖 LangGraph Agentic AI Chatbot

A **production-ready, multi-threaded PDF Q&A chatbot** combining LangGraph agents, LangChain tools, Streamlit frontend, and Google Generative AI.

## ✨ Features

✅ **RAG-Enabled PDF Q&A** - Ask questions about uploaded documents  
✅ **Multi-threaded Conversations** - Isolated conversation contexts per thread  
✅ **Built-in Tools** - Web search, calculator, stock prices, and more  
✅ **Responsive UI** - Mobile-friendly Streamlit interface  
✅ **Persistent Storage** - SQLite database for chat history  
✅ **Real-time Streaming** - Token-by-token response streaming  
✅ **Production-Ready** - Error handling, logging, and configuration management  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.12 recommended)
- Google Generative AI API key ([Get free key](https://aistudio.google.com/app/apikey))

### Installation

```bash
# 1. Navigate to project
cd d:\Agentic\agentic-ai-chatbot

# 2. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Configure API key
copy backend\app\config\.example.env backend\app\config\.env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```

### Run Application

```bash
streamlit run frontend/streamlit/app.py
```

Opens at: **http://localhost:8501**

---

## 📁 Project Structure

```
agentic-ai-chatbot/
├── backend/                    # LangGraph backend
│   ├── app/
│   │   ├── main.py            # Backend entrypoint
│   │   ├── agents/            # LangGraph implementations
│   │   ├── config/            # Environment configuration
│   │   ├── data/              # PDF storage & metadata
│   │   └── services/          # Utility services
│   └── requirements.txt        # Dependencies
├── frontend/streamlit/         # Streamlit UI
│   └── app.py                 # Main responsive app
├── docs/
│   └── project_documentation.md # Detailed setup guide
└── README.md                   # This file
```

---

## 🎯 How to Use

### 1. **Start a New Conversation**
Click **"➕ New Chat"** to create an isolated conversation thread

### 2. **Upload a PDF**
- **Method 1**: Drag & drop in the sidebar, or click "📤 Upload PDF"
- **Method 2**: Enter a PDF URL under "📎 Load from URL"

### 3. **Ask Questions**
Type questions about your document:
- *"What are the main topics?"*
- *"Summarize chapter 2"*
- *"What does page 5 say about..."*

### 4. **Use Built-in Tools**
The AI will automatically use tools when helpful:
- 🔍 Web search for current information
- 🧮 Calculator for math problems
- 📈 Stock price lookups

### 5. **Manage Conversations**
- View past conversations in the sidebar
- Switch between threads instantly
- Delete old conversations with the 🗑️ button

---

## 🔧 Configuration

### Edit `.env` File

```env
# Required
GEMINI_API_KEY=your_actual_key_here

# Optional
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Customize Backend

**Change LLM Model** (in `backend/app/agents/langgraph_backend.py`):
```python
model="gemini-2.5-flash"  # or gemini-1.5-flash, gemini-1.5-pro
temperature=0.7  # 0=deterministic, 1=creative
```

**Adjust PDF Chunking**:
```python
chunk_size=1000  # Increase for longer context windows
chunk_overlap=200  # Overlap for continuity
```

---

## 📊 Architecture

```
User Input (Streamlit UI)
           ↓
    Parse & Thread ID
           ↓
    LangGraph Chatbot
     ↙            ↘
Chat Node      Tools Node
   ↓                ↓
  LLM           RAG/Search/Calc
   ↓                ↓
   └────────┬───────┘
            ↓
    SQLite Checkpoint
            ↓
    Stream Response
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY not found` | Add key to `backend/app/config/.env` |
| `ModuleNotFoundError` | Run `pip install -r backend/requirements.txt` |
| `Streamlit can't find backend` | Run from project root directory |
| PDF upload fails | Ensure PDF is valid (< 50MB recommended) |
| Slow responses | Use `gemini-1.5-flash` for speed |

See **[detailed docs](docs/project_documentation.md)** for more troubleshooting.

---

## 🚀 Deployment

### Local Development
```bash
streamlit run frontend/streamlit/app.py --logger.level=debug
```

### Docker
```bash
docker build -t chatbot:latest .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key chatbot:latest
```

### Cloud (Streamlit Share)
1. Push to GitHub
2. Visit https://share.streamlit.io
3. Select your repo
4. Add `GEMINI_API_KEY` to secrets
5. Deploy instantly ✨

---

## 📚 Key Components

| Component | Purpose | Tech Stack |
|-----------|---------|-----------|
| **Backend** | Agent orchestration & RAG | LangGraph, LangChain, FAISS |
| **Frontend** | User interface | Streamlit, HTML/CSS |
| **Database** | Chat persistence | SQLite, Memory |
| **LLM** | Intelligence & reasoning | Google Generative AI (Gemini) |
| **Tools** | External integrations | DuckDuckGo, Alpha Vantage, Custom |

---

## 💡 Tips & Best Practices

1. **Large PDFs?** Split them into smaller documents for better retrieval
2. **Rate limiting?** Set `max_tokens=512` in config for cost control
3. **Privacy?** Run locally or use environment variables for secrets
4. **Performance?** Use `gemini-1.5-flash` for speed, `gemini-1.5-pro` for quality
5. **Custom tools?** Add new `@tool` functions in `langgraph_backend.py`

---

## 📝 Backend Variants

The project includes multiple backend implementations:

| Backend | Best For | Features |
|---------|----------|----------|
| `langgraph_backend.py` | **Production** ✅ | RAG + All tools |
| `langgraph_database_backend.py` | SQLite persistence | Database storage |
| `langgraph_tool_backend.py` | Simple tools | Calculator, search |
| `langgraph_mcp_backend.py` | Advanced | Model Context Protocol |

---

## 🔐 Security

- ✅ Never commit `.env` to git (in `.gitignore`)
- ✅ Use environment variables for secrets
- ✅ Validate PDF inputs before processing
- ✅ Implement rate limiting for production
- ✅ Use HTTPS for cloud deployments

---

## 📖 Full Documentation

→ **[Complete Setup & Development Guide](docs/project_documentation.md)**

Covers:
- Detailed installation & configuration
- API reference
- Development guide
- Deployment options
- Performance optimization
- Contributing guidelines

---

## 🤝 Contributing

Have improvements? We'd love to see them!

```bash
git checkout -b feature/my-feature
git commit -am 'Add awesome feature'
git push origin feature/my-feature
```

---

## 📧 Support

**Issues or questions?**
1. Check [troubleshooting section](docs/project_documentation.md#-troubleshooting)
2. Review backend logs in terminal
3. Visit [Streamlit docs](https://docs.streamlit.io)
4. Check [LangGraph documentation](https://langchain-ai.github.io/langgraph/)

---

## 📄 License

This project is provided as-is for educational and production use.

---

**Version**: 1.0.0  
**Last Updated**: May 23, 2026  
**Status**: ✅ Production Ready

---

## 🎉 What's Included

- ✅ Complete backend package with package boundary
- ✅ Responsive Streamlit UI with mobile support
- ✅ Comprehensive documentation
- ✅ All dependencies pinned and tested
- ✅ Ready for local or cloud deployment
- ✅ Professional code quality and error handling
- ✅ Multiple backend variants for different use cases

**Ready to chat? Run: `streamlit run frontend/streamlit/app.py` 🚀**
