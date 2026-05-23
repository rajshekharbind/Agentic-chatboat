# LangGraph Agentic AI Chatbot - Complete Setup & Usage Guide

## 📋 Project Overview

This is a **production-ready, multi-threaded PDF Q&A chatbot** built with LangGraph, LangChain, and Streamlit. It combines:

- **Backend**: LangGraph agent with RAG (Retrieval-Augmented Generation), web search, calculator, and stock price tools
- **Frontend**: Responsive Streamlit UI with thread-based conversation management  
- **Database**: SQLite with in-memory fallback for chat persistence
- **LLM**: Google Generative AI (Gemini) with configurable embeddings

---

## 🚀 Quick Start

### 1. Clone/Setup Project
```bash
cd d:\Agentic\agentic-ai-chatbot
```

### 2. Create Virtual Environment (if not already done)
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment
Copy the example config and add your API key:
```bash
copy backend\app\config\.example.env backend\app\config\.env
```

Then edit `backend/app/config/.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
STREAMLIT_SERVER_PORT=8501
```

**Get your API key from:** https://aistudio.google.com/app/apikey

### 5. Run the Application
```bash
streamlit run frontend/streamlit/app.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
agentic-ai-chatbot/
├── backend/                          # Backend package
│   ├── app/
│   │   ├── main.py                   # Backend entrypoint
│   │   ├── agents/
│   │   │   ├── langgraph_backend.py  # ⭐ Main backend (RAG + Tools)
│   │   │   ├── langgraph_rag_backend.py  # Compatibility wrapper
│   │   │   ├── langgraph_database_backend.py
│   │   │   ├── langgraph_tool_backend.py
│   │   │   └── langgraph_mcp_backend.py
│   │   ├── config/
│   │   │   ├── .env                  # ⭐ Add your API key here
│   │   │   └── .example.env          # Example config template
│   │   ├── data/                     # PDF storage & metadata
│   │   ├── database/                 # Chat persistence (SQLite)
│   │   └── services/                 # Utility services
│   ├── requirements.txt              # Python dependencies
│   └── README.md
│
├── frontend/
│   └── streamlit/
│       ├── app.py                    # ⭐ Main Streamlit app (RESPONSIVE UI)
│       ├── streamlit_frontend.py     # Alternative: Basic UI
│       ├── streamlit_frontend_database.py
│       ├── streamlit_frontend_rag.py
│       ├── streamlit_frontend_mcp.py
│       └── ...
│
├── docs/
│   └── project_documentation.md      # This file
│
└── README.md                          # Root documentation
```

---

## 🎯 Key Features

### Backend Features
- **RAG (Retrieval-Augmented Generation)**: Upload PDFs and ask questions about them
- **Multi-threaded Conversations**: Each conversation has its own isolated context
- **Built-in Tools**:
  - 📚 RAG Tool: Vector search over uploaded PDFs
  - 🔍 Web Search: DuckDuckGo search integration
  - 🧮 Calculator: Arithmetic operations
  - 📈 Stock Price Lookup: Real-time stock quotes via Alpha Vantage
- **Persistent Storage**: Chat history saved to SQLite database
- **Google Generative AI**: Uses Gemini 2.5 Flash for fast, intelligent responses

### Frontend Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Thread Management**: 
  - Create new conversations
  - Load past conversations
  - Delete old threads
- **PDF Management**:
  - Upload PDFs directly
  - Load PDFs from URLs
  - Track indexing progress with visual feedback
- **Streaming Responses**: Real-time token streaming for instant feedback
- **Tool Monitoring**: Watch which tools are being used in real-time
- **Professional UI**: Gradient backgrounds, smooth animations, accessible colors

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required: Google Generative AI
GEMINI_API_KEY=your_api_key_from_aistudio.google.com

# Optional: Streamlit Server Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_CLIENT_THEME=light
```

### Customization Options

**Change LLM Model** (in `backend/app/agents/langgraph_backend.py`):
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # or "gemini-1.5-pro", "gemini-1.5-flash"
    api_key=gemini_api_key,
    temperature=0.7,  # Adjust creativity (0-1)
    max_tokens=1024   # Response length limit
)
```

**Adjust PDF Processing** (in `backend/app/agents/langgraph_backend.py`):
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Size of text chunks
    chunk_overlap=200,      # Overlap between chunks
    separators=["\n\n", "\n", " ", ""]  # Splitting strategy
)
```

**Change Database** (in `backend/app/agents/langgraph_backend.py`):
- `MemorySaver()`: In-memory (default, no persistence across restarts)
- `SqliteSaver(conn)`: SQLite database (recommended for production)

---

## 🛠️ Development Guide

### Running Individual Backend Variants

The project includes multiple backend implementations for different use cases:

1. **Main RAG Backend** (RECOMMENDED):
   ```bash
   python -c "from backend.app.main import main; main()"
   ```

2. **Database Backend** (SQLite persistence):
   ```python
   from backend.app.agents.langgraph_database_backend import chatbot
   ```

3. **Tool Backend** (Basic with calculator/search):
   ```python
   from backend.app.agents.langgraph_tool_backend import chatbot
   ```

4. **MCP Backend** (With Model Context Protocol):
   ```python
   from backend.app.agents.langgraph_mcp_backend import chatbot
   ```

### Creating Custom Tools

To add a new tool to the backend, add a function decorated with `@tool`:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input_param: str) -> dict:
    """Tool description for the LLM to understand when to use it."""
    result = process(input_param)
    return {"result": result}

# Add to tools list
tools = [search_tool, my_custom_tool, rag_tool, ...]
```

### Testing Backend

```bash
# Test backend entrypoint
python backend/app/main.py

# Test with custom thread
python -c "
from backend.app.agents.langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
result = chatbot.invoke(
    {'messages': [HumanMessage(content='Hello')]},
    {'configurable': {'thread_id': 'test-123'}}
)
print(result)
"
```

---

## 📊 Deployment Guide

### Local Deployment (Development)
```bash
# Terminal 1: Run backend checks
python backend/app/main.py

# Terminal 2: Run Streamlit UI
streamlit run frontend/streamlit/app.py
```

### Docker Deployment (Production)

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "frontend/streamlit/app.py"]
```

Build and run:
```bash
docker build -t chatbot:latest .
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  chatbot:latest
```

### Cloud Deployment (Streamlit Cloud)

1. Push to GitHub
2. Go to https://share.streamlit.io/
3. Select your repository
4. Set environment variable `GEMINI_API_KEY` in secrets
5. Deploy

---

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution**: Make sure `.env` file exists in `backend/app/config/` and contains your API key:
```bash
echo "GEMINI_API_KEY=your_key" > backend/app/config/.env
```

### Issue: "No module named 'langchain'"
**Solution**: Reinstall dependencies:
```bash
pip install --upgrade -r backend/requirements.txt
```

### Issue: "Streamlit can't find backend package"
**Solution**: Ensure you're running Streamlit from the project root:
```bash
cd d:\Agentic\agentic-ai-chatbot
streamlit run frontend/streamlit/app.py
```

### Issue: PDF upload fails
**Solution**: Ensure the PDF is valid and not corrupted. Try again or use a smaller file.

### Issue: Slow responses
**Solution**: 
- Reduce `chunk_size` in backend for faster retrieval
- Use `gemini-1.5-flash` instead of `gemini-2.5-flash` for speed
- Increase `temperature` to 0.5 for faster generations

---

## 📈 Performance Tips

1. **Increase concurrency**: Streamlit rerun on tool use for instant feedback
2. **Optimize embeddings**: Use smaller embedding models for faster indexing
3. **Cache PDFs**: Store processed PDF vectors for instant retrieval
4. **Use appropriate models**: 
   - `gemini-1.5-flash`: Fast, cost-effective
   - `gemini-2.5-flash`: Balanced quality/speed
   - `gemini-1.5-pro`: Best quality (slower)

---

## 🔐 Security Considerations

- **Never commit `.env` files** to version control
- **Use environment variables** for all secrets
- **Validate user inputs** before processing PDFs
- **Implement rate limiting** for production deployments
- **Use HTTPS** for cloud deployments
- **Sanitize PDF content** for sensitive documents

---

## 📚 API Reference

### Backend Functions

#### `ingest_pdf(file_bytes, thread_id, filename)`
Indexes a PDF for RAG retrieval.
```python
from backend.app.agents.langgraph_backend import ingest_pdf

summary = ingest_pdf(
    file_bytes=pdf_content,
    thread_id="user-thread-1",
    filename="document.pdf"
)
# Returns: {"filename": "...", "documents": 5, "chunks": 42}
```

#### `retrieve_all_threads()`
Lists all saved conversation threads.
```python
from backend.app.agents.langgraph_backend import retrieve_all_threads

threads = retrieve_all_threads()
# Returns: ["thread-1", "thread-2", ...]
```

#### `thread_document_metadata(thread_id)`
Gets PDF metadata for a specific thread.
```python
from backend.app.agents.langgraph_backend import thread_document_metadata

metadata = thread_document_metadata("thread-1")
# Returns: {"filename": "doc.pdf", "documents": 5, "chunks": 42}
```

---

## 📝 License & Attribution

This project uses:
- **LangGraph**: Agentic orchestration framework
- **LangChain**: LLM framework
- **Streamlit**: Web UI framework
- **Google Generative AI**: LLM provider
- **FAISS**: Vector database

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/my-feature`
4. Create a Pull Request

---

## 📧 Support

For issues or questions:
- Check troubleshooting section above
- Review backend logs in terminal
- Check Streamlit documentation at https://docs.streamlit.io
- Visit LangGraph docs at https://langchain-ai.github.io/langgraph/

---

**Last Updated**: May 23, 2026  
**Version**: 1.0.0 (Production Ready)
