"""
Flask web server for LangGraph PDF Chatbot
Serves HTML/Tailwind CSS frontend + REST API
"""

import os
import sys
import json
import uuid
from pathlib import Path

# Add project root to path FIRST, before any imports
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import backend
try:
    from backend.app.agents.langgraph_backend import (
        chatbot,
        ingest_pdf,
        retrieve_all_threads,
        thread_document_metadata,
        get_thread_messages,
    )
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError as e:
    print(f"❌ Backend import error: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent / "data" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max


# ============================================
# Frontend Routes
# ============================================

@app.route('/', methods=['GET'])
def index():
    """Serve main HTML page."""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve static files."""
    if path != '' and os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    return send_from_directory('static', 'index.html')


# ============================================
# Health & Status Endpoints
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'LangGraph API is running',
        'backend': 'ready'
    }), 200


@app.route('/api/status', methods=['GET'])
def status():
    """Get current API status."""
    try:
        threads = retrieve_all_threads()
        return jsonify({
            'status': 'ready',
            'threads': len(list(threads)) if threads else 0,
            'uploads': len(list(UPLOAD_FOLDER.glob('*.pdf')))
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500


# ============================================
# Chat Endpoints
# ============================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Submit a message and get AI response."""
    print("=" * 60)
    print("📥 CHAT ENDPOINT CALLED")
    print("=" * 60)
    
    try:
        data = request.get_json()
        print(f"✅ Request data: {data}")
        
        if not data:
            print("❌ No JSON data")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        message = data.get('message', '').strip()
        thread_id = data.get('thread_id', str(uuid.uuid4()))
        
        print(f"📝 Message: {message}")
        print(f"🧵 Thread: {thread_id}")
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create config for thread persistence
        config = {'configurable': {'thread_id': thread_id}}
        
        print(f"🤔 Invoking chatbot...")
        from langchain_core.messages import HumanMessage
        
        response = chatbot.invoke(
            {'messages': [HumanMessage(content=message)]},
            config=config
        )
        
        print(f"✅ Got response from chatbot")
        print(f"Response type: {type(response)}")
        print(f"Response keys: {response.keys() if isinstance(response, dict) else 'N/A'}")
        
        # Extract assistant message
        result_text = "I received your message but couldn't generate a response."
        
        if isinstance(response, dict) and 'messages' in response:
            messages = response['messages']
            if isinstance(messages, list) and len(messages) > 0:
                last_msg = messages[-1]
                
                # Handle different message formats
                if hasattr(last_msg, 'content'):
                    result_text = last_msg.content
                elif isinstance(last_msg, dict) and 'content' in last_msg:
                    result_text = last_msg['content']
                
                print(f"✅ Extracted response: {str(result_text)[:100]}...")
        
        print(f"✅ Returning response")
        print("=" * 60)
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'message': message,
            'response': result_text
        }), 200
        
    except Exception as e:
        print(f"❌ ERROR in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/threads', methods=['GET'])
def get_threads():
    """Get all conversation threads."""
    try:
        threads_list = retrieve_all_threads()
        threads = list(threads_list) if threads_list else []
        
        return jsonify({
            'success': True,
            'threads': threads,
            'count': len(threads)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/thread/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get specific thread conversation history."""
    print(f"[THREAD-HISTORY] Loading thread: {thread_id}")
    try:
        # Get actual conversation messages from checkpointer
        raw_messages = get_thread_messages(thread_id)
        
        # Get document metadata
        thread_data = thread_document_metadata(thread_id)
        
        print(f"[THREAD-HISTORY] Found {len(raw_messages) if raw_messages else 0} messages")
        
        # Serialize messages with proper format for frontend
        messages = []
        
        if raw_messages:
            for msg in raw_messages:
                try:
                    # Handle LangChain BaseMessage objects
                    if hasattr(msg, 'type'):
                        # BaseMessage object
                        role_map = {
                            'human': 'user',
                            'ai': 'assistant',
                            'system': 'system',
                            'tool': 'assistant'
                        }
                        messages.append({
                            'role': role_map.get(msg.type, 'assistant'),
                            'content': msg.content if hasattr(msg, 'content') else str(msg),
                        })
                    elif isinstance(msg, dict):
                        # Already a dict - check if it has the right format
                        if 'role' in msg and 'content' in msg:
                            messages.append(msg)
                        elif 'type' in msg:
                            # LangChain message format - map type to role
                            role_map = {
                                'human': 'user',
                                'ai': 'assistant',
                                'system': 'system',
                                'tool': 'assistant'
                            }
                            messages.append({
                                'role': role_map.get(msg.get('type'), 'assistant'),
                                'content': msg.get('content', ''),
                            })
                        else:
                            # Unknown format - try to extract content
                            messages.append({
                                'role': 'assistant',
                                'content': str(msg.get('content', msg))
                            })
                    else:
                        # Try to get content as string
                        messages.append({
                            'role': 'assistant',
                            'content': str(msg)
                        })
                except Exception as msgError:
                    print(f"[THREAD-HISTORY] Error serializing message: {msgError}")
                    continue
        
        print(f"[THREAD-HISTORY] Returning {len(messages)} serialized messages")
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'messages': messages,
            'documents': thread_data.get('documents', []),
            'messageCount': len(messages)
        }), 200
    except Exception as e:
        print(f"[THREAD-HISTORY] Error loading thread {thread_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e), 
            'thread_id': thread_id,
            'messages': [],
            'documents': []
        }), 500


@app.route('/api/thread/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """Delete a thread."""
    try:
        metadata_file = Path(PROJECT_ROOT) / "backend" / "app" / "data" / "thread_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if thread_id in metadata:
                del metadata[thread_id]
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Thread {thread_id} deleted'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# PDF Endpoints
# ============================================

@app.route('/api/pdf/upload', methods=['POST'])
def upload_pdf():
    """Upload PDF file for ingestion."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        thread_id = request.form.get('thread_id', str(uuid.uuid4()))
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save file
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(filepath))
        
        # Ingest PDF
        try:
            result = ingest_pdf(str(filepath), thread_id)
            result_msg = f"✅ PDF ingested successfully"
        except Exception as ingest_err:
            result_msg = f"⚠️ PDF processed with status: {str(ingest_err)[:100]}"
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'filename': file.filename,
            'filepath': str(filepath),
            'message': result_msg
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/pdf/from-url', methods=['POST'])
def upload_pdf_from_url():
    """Download and ingest PDF from URL."""
    try:
        import requests
        
        data = request.get_json()
        url = data.get('url', '').strip()
        thread_id = data.get('thread_id', str(uuid.uuid4()))
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Download PDF
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return jsonify({'error': f'Failed to download: {response.status_code}'}), 400
        
        # Save to temp file
        filename = f"{uuid.uuid4()}_downloaded.pdf"
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Ingest PDF
        try:
            result = ingest_pdf(str(filepath), thread_id)
            result_msg = f"✅ PDF from URL ingested successfully"
        except Exception as ingest_err:
            result_msg = f"⚠️ PDF processed with status: {str(ingest_err)[:100]}"
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'url': url,
            'message': result_msg
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return send_from_directory('static', 'index.html')


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("🚀 LangGraph PDF Chatbot - HTML/Tailwind Frontend")
    print("="*60)
    print(f"🌐 Web URL: http://0.0.0.0:{port}")
    print(f"📍 API URL: http://0.0.0.0:{port}/api")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
