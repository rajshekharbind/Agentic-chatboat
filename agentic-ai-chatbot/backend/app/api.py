"""
Flask API server for LangGraph PDF Chatbot
Exposes backend functionality through REST API endpoints
"""

import os
import json
import uuid
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment
load_dotenv()

# Import backend
try:
    from backend.app.agents.langgraph_backend import (
        chatbot,
        ingest_pdf,
        retrieve_all_threads,
        thread_document_metadata,
    )
except ImportError as e:
    print(f"❌ Backend import error: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent / "data" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max


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
    return jsonify({
        'status': 'ready',
        'threads': len(retrieve_all_threads()),
        'uploads': len(list(UPLOAD_FOLDER.glob('*.pdf')))
    }), 200


# ============================================
# Chat Endpoints
# ============================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Submit a message and get AI response."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        thread_id = data.get('thread_id', str(uuid.uuid4()))
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Invoke chatbot
        config = {'configurable': {'thread_id': thread_id}}
        
        response = chatbot.invoke(
            {'messages': [{'role': 'user', 'content': message}]},
            config=config
        )
        
        # Extract assistant message
        result_text = ""
        if 'messages' in response:
            for msg in response['messages']:
                if hasattr(msg, 'content') and msg.__class__.__name__ == 'AIMessage':
                    result_text = msg.content
                    break
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'message': message,
            'response': result_text,
            'timestamp': str(Path(__file__).stat().st_mtime)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/threads', methods=['GET'])
def get_threads():
    """Get all conversation threads."""
    try:
        threads = retrieve_all_threads()
        return jsonify({
            'success': True,
            'threads': list(threads),
            'count': len(threads)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/thread/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get specific thread conversation history."""
    print(f"DEBUG: Getting thread: {thread_id}")  # Debug marker
    try:
        # Pass thread_id to the function
        thread_data = thread_document_metadata(thread_id)
        print(f"DEBUG: Got thread data with {len(thread_data.get('messages', []))} messages")
        
        # Serialize messages with proper format for frontend
        messages = []
        raw_messages = thread_data.get('messages', [])
        
        if raw_messages:
            for msg in raw_messages:
                # Handle different message formats
                if isinstance(msg, dict):
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
                            'type': msg.get('type')
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
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'messages': messages,
            'documents': thread_data.get('documents', [])
        }), 200
    except Exception as e:
        print(f"Error in get_thread: {str(e)}")
        return jsonify({'error': str(e), 'thread_id': thread_id}), 500


@app.route('/api/thread/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """Delete a thread."""
    try:
        metadata = thread_document_metadata()
        if thread_id in metadata:
            del metadata[thread_id]
            
            # Save updated metadata
            metadata_file = Path(__file__).parent / "data" / "thread_metadata.json"
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
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save file
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        # Ingest PDF
        result = ingest_pdf(str(filepath), thread_id)
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'filename': file.filename,
            'filepath': str(filepath),
            'message': f'PDF ingested successfully',
            'result': str(result)
        }), 200
        
    except Exception as e:
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
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Ingest PDF
        result = ingest_pdf(str(filepath), thread_id)
        
        return jsonify({
            'success': True,
            'thread_id': thread_id,
            'url': url,
            'message': 'PDF ingested successfully',
            'result': str(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Starting LangGraph API Server...")
    print("📍 API URL: http://localhost:5000")
    print("📚 Docs: http://localhost:5000/api/docs")
    app.run(debug=True, host='0.0.0.0', port=5000)
