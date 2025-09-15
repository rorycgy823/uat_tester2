#!/usr/bin/env python3
"""
Conversational Qwen 1.5 1.8B GGUF Model Server
===============================================

A Flask application with a chat UI to interact with a Qwen 1.5 1.8B GGUF model.
This version supports conversation history, session management,
and adjustable parameters including dynamic prompt templates.
"""

import os
import logging
import io
import sys
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.serving import ThreadedWSGIServer
from werkzeug.utils import secure_filename
import socket
import shelve
from datetime import datetime
import json

# --- GraphRAG Imports ---
try:
    from graph_rag import GraphRAGProcessor, ChromaDBManager
    GRAPH_RAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"GraphRAG components not available: {e}")
    GRAPH_RAG_AVAILABLE = False

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- App Setup ---
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'

# --- Global variables ---
llm = None
PROMPT_TEMPLATE = "Instruct: {prompt}\nOutput:"
SYSTEM_PROMPT = """You are a helpful AI assistant specialized in UAT (User Acceptance Testing) and software quality assurance. 
You excel at generating comprehensive test cases from user stories, identifying test variables, and providing detailed testing guidance.

When generating test cases:
1. Consider both happy path and edge cases
2. Include functional, regression, and integration testing scenarios
3. Identify specific UI elements, data inputs, and expected outcomes
4. Structure test cases with clear steps and expected results

When helping with general questions:
1. Provide clear, concise, and accurate information
2. If you're unsure about something, admit it rather than guess
3. Focus on practical solutions and best practices
"""

# --- Server-side Session Storage ---
SESSION_DB = 'sessions.db'
UAT_SESSION_DB = 'uat_sessions.db'

def get_all_sessions():
    """Get all chat sessions from server-side storage"""
    with shelve.open(SESSION_DB) as db:
        return sorted(db.keys(), reverse=True)

def save_session(session_id, history, timings=''):
    """Save chat session to server-side storage"""
    with shelve.open(SESSION_DB) as db:
        db[session_id] = {
            'history': history,
            'timings': timings,
            'timestamp': datetime.now().isoformat()
        }

def load_session(session_id):
    """Load chat session from server-side storage"""
    with shelve.open(SESSION_DB) as db:
        session_data = db.get(session_id, {})
        return session_data.get('history', []), session_data.get('timings', '')

def delete_session(session_id):
    """Delete a specific session from server-side storage"""
    with shelve.open(SESSION_DB) as db:
        if session_id in db:
            del db[session_id]

def cleanup_old_sessions(max_age_days=30):
    """Clean up sessions older than max_age_days"""
    with shelve.open(SESSION_DB) as db:
        keys_to_delete = []
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for key in db.keys():
            session_data = db[key]
            timestamp = session_data.get('timestamp', '')
            if timestamp:
                try:
                    session_time = datetime.fromisoformat(timestamp).timestamp()
                    if session_time < cutoff_time:
                        keys_to_delete.append(key)
                except ValueError:
                    # If we can't parse the timestamp, mark for deletion
                    keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del db[key]

# --- GraphRAG Components ---
if GRAPH_RAG_AVAILABLE:
    try:
        graph_rag_processor = GraphRAGProcessor()
        chroma_db_manager = ChromaDBManager()
        logger.info("✅ GraphRAG components initialized successfully!")
    except Exception as e:
        logger.warning(f"Failed to initialize GraphRAG components: {e}")
        GRAPH_RAG_AVAILABLE = False
else:
    graph_rag_processor = None
    chroma_db_manager = None

# --- Session Management ---
# Using the server-side session storage functions defined above

# --- Model Loading ---
def load_model():
    global llm
    try:
        from llama_cpp import Llama
    except ImportError:
        logger.error("FATAL: llama-cpp-python library not found.")
        return False

    model_filename = "qwen1.5-1.8b.Q4_K_M.gguf"  # Updated for Qwen 1.5 1.8B model
    model_path = None
    possible_paths = [
        model_filename,
        f"/home/cdsw/{model_filename}",
        f"/home/cdsw/models/{model_filename}",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            logger.info(f"Found GGUF model at: {model_path}")
            break
            
    if not model_path:
        logger.error(f"FATAL: Could not find the model file '{model_filename}'.")
        return False

    try:
        logger.info("Loading Qwen 1.5 1.8B GGUF model with llama-cpp-python...")
        llm = Llama(
            model_path=model_path,
            n_ctx=32768,  # Increased context window size to 32K for Qwen model
            n_threads=8,  # Increased threads to match your 8-core CPU
            n_gpu_layers=0
        )
        logger.info("✅ Model loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"FATAL: Failed to load the model with llama-cpp-python.")
        logger.error(f"Error details: {e}")
        return False

# --- Main Chat Logic ---
def generate_response(prompt, max_tokens):
    history = session.get('chat_history', [])
    
    # Construct the full prompt with system prompt and conversation history
    full_prompt_parts = []
    
    # Add system prompt if it exists
    if SYSTEM_PROMPT:
        full_prompt_parts.append(SYSTEM_PROMPT)
    
    # Add conversation history
    full_prompt_parts.extend(history)
    
    # Use the global prompt template for the current prompt
    formatted_prompt = PROMPT_TEMPLATE.format(prompt=prompt)
    full_prompt_parts.append(formatted_prompt)
    
    full_prompt = "\n".join(full_prompt_parts)
    
    logger.info(f"Generating response with max_tokens={max_tokens}...")

    # Capture llama_print_timings
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        output = llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["</end>", "[END]", "Instruct:"]
        )
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        sys.stdout = old_stdout
        error_message = f"Error generating response: {str(e)}"
        history.append(error_message)
        session['chat_history'] = history
        return error_message

    sys.stdout = old_stdout
    timings = captured_output.getvalue()
    logger.info(f"Performance Timings:\n{timings}")
    
    answer = output["choices"][0]["text"].strip()
    history.append(answer)
    session['chat_history'] = history
    session['timings'] = timings # Store timings in session
    
    return answer

# --- Web UI Routes ---
@app.route('/')
def main_page():
    if 'session_id' not in session:
        # Initialize a new session
        session['session_id'] = None
        session['chat_history'] = []
        session['timings'] = ''
    
    return render_template("index.html", 
                           sessions=get_all_sessions(),
                           current_session_id=session.get('session_id'),
                           history=session.get('chat_history', []),
                           timings=session.get('timings', ''))

@app.route('/new_chat')
def new_chat():
    # Save the old session before creating a new one
    history = session.get('chat_history', [])
    timings = session.get('timings', '')
    if history:
        session_id = session.get('session_id')
        if not session_id:
            first_prompt = history[0].replace('Instruct:', '').replace('\nOutput:', '').strip()
            safe_name = secure_filename(first_prompt[:30])
            session_id = f"{datetime.now().strftime('%Y%m%d-%H%M')}_{safe_name}"
        save_session(session_id, history, timings)

    # Clear the session to start fresh
    session.pop('session_id', None)
    session.pop('chat_history', None)
    session.pop('timings', None)
    return redirect(url_for('main_page'))

@app.route('/session/<session_id>')
def view_session(session_id):
    session['session_id'] = session_id
    history, timings = load_session(session_id)
    session['chat_history'] = history
    session['timings'] = timings
    return redirect(url_for('main_page'))

@app.route('/ask', methods=['POST'])
def ask_question():
    if llm is None: return "Model is not loaded.", 503

    prompt = request.form.get('prompt', '')
    max_tokens = int(request.form.get('max_tokens', 1024))  # Increased default value
    
    if not prompt: return "Please provide a prompt.", 400

    generate_response(prompt, max_tokens)
    
    return redirect(url_for('main_page'))

@app.route('/save_session', methods=['POST'])
def save_current_session():
    """Saves the current chat history with a user-friendly, URL-safe name."""
    history = session.get('chat_history', [])
    timings = session.get('timings', '')
    if history:
        # Use existing session_id if it's already saved, otherwise create a new one
        session_id = session.get('session_id')
        if not session_id:
            first_prompt = history[0].replace('Instruct:', '').replace('\nOutput:', '').strip()
            safe_name = secure_filename(first_prompt[:30])
            session_id = f"{datetime.now().strftime('%Y%m%d-%H%M')}_{safe_name}"
        
        save_session(session_id, history, timings)
        session['session_id'] = session_id # Ensure session_id is set
        
    return redirect(url_for('main_page'))

@app.route('/delete_session/<session_id>', methods=['GET'])
def delete_session_route(session_id):
    """Deletes a specific session."""
    active_session_id = session.get('session_id')
    delete_session(session_id)
    # If the deleted session was the active one, start a new chat
    if active_session_id == session_id:
        return redirect(url_for('new_chat'))
    return redirect(url_for('main_page'))

@app.route('/settings', methods=['GET'])
def settings_page():
    """Displays the settings page."""
    # Ensure the global variables are passed correctly
    return render_template("settings.html", prompt_template=PROMPT_TEMPLATE, system_prompt=SYSTEM_PROMPT)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Updates the global prompt template."""
    global PROMPT_TEMPLATE
    new_template = request.form.get('prompt_template')
    if new_template:
        PROMPT_TEMPLATE = new_template
    return redirect(url_for('settings_page'))

@app.route('/update_system_prompt', methods=['POST'])
def update_system_prompt():
    """Updates the global system prompt."""
    global SYSTEM_PROMPT
    new_system_prompt = request.form.get('system_prompt')
    if new_system_prompt is not None:  # Allow empty system prompts
        SYSTEM_PROMPT = new_system_prompt
    return redirect(url_for('settings_page'))

# --- UAT Testing with GraphRAG Routes ---
@app.route('/uat')
def uat_page():
    """Displays the UAT testing page."""
    if not GRAPH_RAG_AVAILABLE:
        return "GraphRAG components are not available.", 503
    
    # Initialize UAT session data if not present
    if 'uat_test_cases' not in session:
        session['uat_test_cases'] = []
    if 'uat_variables' not in session:
        session['uat_variables'] = {}
    
    return render_template("uat.html", 
                           test_cases=session.get('uat_test_cases', []),
                           variables=session.get('uat_variables', {}))

@app.route('/uat/generate_test_cases', methods=['POST'])
def generate_test_cases():
    """Generate test cases from user story using GraphRAG."""
    if not GRAPH_RAG_AVAILABLE:
        return "GraphRAG components are not available.", 503
    
    user_story = request.form.get('user_story', '')
    if not user_story:
        return "Please provide a user story.", 400
    
    try:
        # Query ChromaDB for similar historical cases
        similar_cases = chroma_db_manager.query_documents(user_story, n_results=3)
        
        # Generate test cases using GraphRAG
        test_cases = graph_rag_processor.generate_test_cases(user_story, similar_cases)
        
        # Identify test variables
        variables = graph_rag_processor.identify_test_variables(test_cases)
        
        # Store in session
        session['uat_test_cases'] = test_cases
        session['uat_variables'] = variables
        session['uat_user_story'] = user_story
        
        return redirect(url_for('uat_page'))
    except Exception as e:
        logger.error(f"Error generating test cases: {e}")
        return f"Error generating test cases: {e}", 500

@app.route('/uat/save_test_case', methods=['POST'])
def save_test_case():
    """Save a test case to ChromaDB."""
    if not GRAPH_RAG_AVAILABLE:
        return "GraphRAG components are not available.", 503
    
    try:
        test_case_data = request.get_json()
        if not test_case_data:
            return "No test case data provided.", 400
        
        # Add to ChromaDB
        success = chroma_db_manager.add_documents([{
            'id': test_case_data.get('id', ''),
            'content': test_case_data.get('description', ''),
            'metadata': {
                'test_case': test_case_data,
                'type': 'uat_test_case'
            }
        }])
        
        if success:
            return jsonify({"status": "success", "message": "Test case saved successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to save test case"}), 500
    except Exception as e:
        logger.error(f"Error saving test case: {e}")
        return jsonify({"status": "error", "message": f"Error saving test case: {e}"}), 500

@app.route('/uat/configure_variables', methods=['POST'])
def configure_variables():
    """Configure test variables for execution."""
    if not GRAPH_RAG_AVAILABLE:
        return "GraphRAG components are not available.", 503
    
    try:
        variables_data = request.get_json()
        if not variables_data:
            return "No variables data provided.", 400
        
        # Store configured variables in session
        session['uat_variables'] = variables_data
        
        return jsonify({"status": "success", "message": "Variables configured successfully"})
    except Exception as e:
        logger.error(f"Error configuring variables: {e}")
        return jsonify({"status": "error", "message": f"Error configuring variables: {e}"}), 500

# --- Custom Server with Port Reuse ---
class ReusableThreadedWSGIServer(ThreadedWSGIServer):
    def __init__(self, host, port, app):
        super().__init__(host, port, app)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if __name__ == '__main__':
    model_loaded = load_model()
    
    if model_loaded:
        host = os.environ.get('CDSW_IP_ADDRESS', '127.0.0.1')
        port = int(os.environ.get('CDSW_APP_PORT', 8080))
        
        logger.info(f"Starting Flask server on {host}:{port}")
        httpd = ReusableThreadedWSGIServer(host, port, app)
        httpd.serve_forever()
    else:
        logger.error("Application cannot start because the model failed to load.")
        exit(1)
