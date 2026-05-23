"""
LangGraph PDF Chatbot - Streamlit Frontend
A responsive, production-ready UI for multi-document Q&A with LLM agents.
"""

import os
import sys
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from io import BytesIO
import requests

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure Streamlit page
st.set_page_config(
    page_title="LangGraph PDF Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment
load_dotenv()

# ============================================
# BACKEND IMPORTS
# ============================================
try:
    from backend.app.agents.langgraph_backend import (
        chatbot,
        ingest_pdf,
        retrieve_all_threads,
        thread_document_metadata,
    )
    BACKEND_READY = True
except ImportError as e:
    BACKEND_READY = False
    BACKEND_ERROR = str(e)


# ============================================
# CUSTOM CSS FOR RESPONSIVE DESIGN
# ============================================
st.markdown(
    """
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #2ca02c;
        --error-color: #d62728;
        --warning-color: #ff7f0e;
        --success-color: #2ca02c;
        --neutral-color: #7f7f7f;
    }
    
    .main {
        max-width: 100%;
        padding: 1.5rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: var(--primary-color);
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: clamp(1.5rem, 5vw, 2.5rem);
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid var(--primary-color);
        margin-bottom: 2rem;
    }
    
    /* Chat Messages */
    .stChatMessage {
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
    }
    
    /* Input Area */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        outline: none;
    }
    
    /* Sidebar */
    .stSidebar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
    }
    
    .stSidebar h2 {
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .stSidebar .stButton > button {
        background-color: white;
        color: var(--primary-color);
        margin-bottom: 0.75rem;
    }
    
    /* Status and Info Boxes */
    .stSuccess {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 4px solid var(--success-color);
    }
    
    .stError {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border-left: 4px solid var(--error-color);
    }
    
    .stInfo {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border-left: 4px solid var(--primary-color);
    }
    
    .stWarning {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border-left: 4px solid var(--warning-color);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main {
            padding: 1rem 0.5rem;
        }
        
        h1 {
            font-size: 1.75rem;
            margin-bottom: 1rem;
        }
        
        .stChatMessage {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
        }
        
        .stSidebar {
            padding: 1rem 0.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .main {
            padding: 0.75rem 0.25rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        .stChatMessage {
            padding: 0.5rem;
            font-size: 0.9rem;
        }
    }
    
    /* Thread List */
    .thread-button {
        width: 100%;
        text-align: left;
        margin-bottom: 0.5rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Loading Indicator */
    .loading {
        display: inline-block;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================
# BACKEND HEALTH CHECK
# ============================================
if not BACKEND_READY:
    st.error(f"⚠️ Backend initialization failed: {BACKEND_ERROR}")
    st.info("Please ensure all dependencies are installed: `pip install -r backend/requirements.txt`")
    st.stop()


# ============================================
# UTILITY FUNCTIONS
# ============================================
def generate_thread_id() -> str:
    """Generate a unique thread ID for each conversation."""
    return str(uuid.uuid4())


def reset_chat() -> None:
    """Create a new conversation thread."""
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []
    st.session_state["ingested_docs"] = {}


def add_thread(thread_id: str) -> None:
    """Add a thread to the chat history."""
    if thread_id not in st.session_state.get("chat_threads", []):
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id: str) -> list:
    """Load conversation history for a thread."""
    try:
        state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
        return state.values.get("messages", [])
    except Exception as e:
        st.warning(f"⚠️ Could not load conversation: {e}")
        return []


def delete_thread(thread_id: str) -> None:
    """Delete a thread from history."""
    if thread_id in st.session_state.get("chat_threads", []):
        st.session_state["chat_threads"].remove(thread_id)
        if st.session_state.get("thread_id") == thread_id:
            reset_chat()


# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    try:
        st.session_state["chat_threads"] = retrieve_all_threads()
    except Exception:
        st.session_state["chat_threads"] = []

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}

add_thread(st.session_state["thread_id"])


# ============================================
# MAIN LAYOUT
# ============================================

# Header
st.markdown("<h1>🤖 LangGraph PDF Chatbot</h1>", unsafe_allow_html=True)

# Main Container with two columns
col_main, col_sidebar = st.columns([3, 1])

with col_sidebar:
    st.sidebar.title("📋 Sidebar")

# Sidebar Content
with st.sidebar:
    st.markdown("### 🆕 Start New Conversation")
    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()
        st.rerun()
    
    st.divider()
    
    # Display Current Thread ID
    thread_key = str(st.session_state["thread_id"])
    st.markdown(f"**Thread ID:** `{thread_key[:12]}...`")
    
    # Document Status
    thread_docs = st.session_state["ingested_docs"].get(thread_key, {})
    if thread_docs:
        latest_doc = list(thread_docs.values())[-1] if thread_docs else None
        if latest_doc:
            st.success(
                f"📄 **{latest_doc.get('filename')}**\n"
                f"Pages: {latest_doc.get('documents')} | Chunks: {latest_doc.get('chunks')}"
            )
    else:
        st.info("📭 No PDF indexed for this chat yet.")
    
    st.divider()
    
    # PDF Upload Section
    st.markdown("### 📤 Upload PDF")
    pdf_source = st.radio("Choose source:", ["File", "URL"], horizontal=True)
    
    if pdf_source == "File":
        uploaded_pdf = st.file_uploader("Select PDF file", type=["pdf"], key="pdf_upload")
        if uploaded_pdf:
            if uploaded_pdf.name not in thread_docs:
                with st.status("🔄 Indexing PDF…", expanded=True):
                    try:
                        summary = ingest_pdf(
                            uploaded_pdf.getvalue(),
                            thread_id=st.session_state["thread_id"],
                            filename=uploaded_pdf.name,
                        )
                        if st.session_state["thread_id"] not in st.session_state["ingested_docs"]:
                            st.session_state["ingested_docs"][st.session_state["thread_id"]] = {}
                        st.session_state["ingested_docs"][st.session_state["thread_id"]][uploaded_pdf.name] = summary
                        st.success(f"✅ Added: {uploaded_pdf.name}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.info(f"✓ `{uploaded_pdf.name}` already processed.")
    
    elif pdf_source == "URL":
        pdf_url = st.text_input("PDF URL", placeholder="https://example.com/doc.pdf")
        if st.button("📥 Load PDF", use_container_width=True):
            if pdf_url.strip():
                with st.status("🔄 Loading PDF…", expanded=True):
                    try:
                        response = requests.get(pdf_url, timeout=30)
                        response.raise_for_status()
                        pdf_bytes = BytesIO(response.content)
                        filename = pdf_url.split("/")[-1]
                        if not filename.endswith(".pdf"):
                            filename = f"document_{len(thread_docs) + 1}.pdf"
                        summary = ingest_pdf(
                            pdf_bytes.getvalue(),
                            thread_id=st.session_state["thread_id"],
                            filename=filename,
                        )
                        if st.session_state["thread_id"] not in st.session_state["ingested_docs"]:
                            st.session_state["ingested_docs"][st.session_state["thread_id"]] = {}
                        st.session_state["ingested_docs"][st.session_state["thread_id"]][filename] = summary
                        st.success(f"✅ Added: {filename}")
                        st.rerun()
                    except requests.exceptions.MissingSchema:
                        st.error("❌ Invalid URL. Use http:// or https://")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a URL")
    
    st.divider()
    
    # Conversation History
    st.markdown("### 📜 Conversations")
    threads = st.session_state["chat_threads"][::-1]
    
    if not threads:
        st.caption("No conversations yet")
    else:
        for thread_id in threads:
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(str(thread_id)[:12], key=f"thread-{thread_id}", use_container_width=True):
                    st.session_state["thread_id"] = thread_id
                    messages = load_conversation(thread_id)
                    temp_messages = []
                    for msg in messages:
                        from langchain_core.messages import HumanMessage
                        role = "user" if isinstance(msg, HumanMessage) else "assistant"
                        temp_messages.append({"role": role, "content": msg.content})
                    st.session_state["message_history"] = temp_messages
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete-{thread_id}"):
                    delete_thread(thread_id)
                    st.rerun()


# Main Chat Area
st.markdown("### 💬 Chat")

# Display message history
chat_container = st.container()
with chat_container:
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])


# User Input
user_input = st.chat_input("Ask about your PDF or use the tools...", key="user_input")

if user_input:
    # Add user message to history
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    # Process with backend
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }
    
    with st.chat_message("assistant"):
        try:
            from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
            
            status_holder = {"box": None}
            
            def ai_only_stream():
                for message_chunk, _ in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode="messages",
                ):
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        if status_holder["box"] is None:
                            status_holder["box"] = st.status(
                                f"🔧 Using `{tool_name}` …", expanded=True
                            )
                        else:
                            status_holder["box"].update(
                                label=f"🔧 Using `{tool_name}` …",
                                state="running",
                                expanded=True,
                            )
                    
                    if isinstance(message_chunk, AIMessage):
                        yield message_chunk.content
            
            ai_message = st.write_stream(ai_only_stream())
            
            if status_holder["box"] is not None:
                status_holder["box"].update(
                    label="✅ Tool finished", state="complete", expanded=False
                )
            
            # Add assistant message to history
            st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# Footer
st.divider()
st.caption("💡 Tip: Upload a PDF to ask questions about its content using AI.")
st.caption("🔗 Built with LangGraph, Streamlit, and Google Generative AI")
