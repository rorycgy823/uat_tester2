#!/usr/bin/env python3
"""
Conversational Phi-2 GGUF Model Server
=======================================

A Flask application with a chat UI to interact with a GGUF model.
This version supports conversation history, session management,
and adjustable parameters including dynamic prompt templates.
"""

import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.serving import ThreadedWSGIServer
from werkzeug.utils import secure_filename
import socket
import shelve
from datetime import datetime

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- App Setup ---
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'supersecretkey'

# --- Global variables ---
llm = None
PROMPT_TEMPLATE = "Instruct: {prompt}\nOutput:"

# --- Session Management ---
SESSION_DB = 'sessions.db'

def get_all_sessions():
    with shelve.open(SESSION_DB) as db:
        return sorted(db.keys(), reverse=True)

def save_session(session_id, history):
    with shelve.open(SESSION_DB) as db:
        db[session_id] = history

def load_session(session_id):
    with shelve.open(SESSION_DB) as db:
        return db.get(session_id, [])

def delete_session(session_id):
    with shelve.open(SESSION_DB) as db:
        if session_id in db:
            del db[session_id]

# --- Model Loading ---
def load_model():
    global llm
    try:
        from llama_cpp import Llama
    except ImportError:
        logger.error("FATAL: llama-cpp-python library not found.")
        return False

    model_filename = "phi-2.Q4_K_M.gguf"
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
        logger.info("Loading Phi-2 GGUF model with llama-cpp-python...")
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
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
    
    # Use the global prompt template
    formatted_prompt = PROMPT_TEMPLATE.format(prompt=prompt)
    history.append(formatted_prompt)
    
    full_prompt = "\n".join(history)
    
    logger.info(f"Generating response with max_tokens={max_tokens}...")
    
    output = llm(
        full_prompt,
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.1,
        stop=["</end>", "[END]", "Instruct:"]
    )
    
    answer = output["choices"][0]["text"].strip()
    history.append(answer)
    session['chat_history'] = history
    
    return answer

# --- Web UI Routes ---
@app.route('/')
def main_page():
    if 'session_id' not in session or not session['session_id']:
        # Start a new, unsaved session
        session['session_id'] = None 
        session['chat_history'] = []
    
    return render_template("index.html", 
                           sessions=get_all_sessions(),
                           current_session_id=session.get('session_id'),
                           history=session.get('chat_history', []))

@app.route('/new_chat')
def new_chat():
    session.pop('session_id', None)
    session.pop('chat_history', None)
    return redirect(url_for('main_page'))

@app.route('/session/<session_id>')
def view_session(session_id):
    session['session_id'] = session_id
    session['chat_history'] = load_session(session_id)
    return redirect(url_for('main_page'))

@app.route('/ask', methods=['POST'])
def ask_question():
    if llm is None: return "Model is not loaded.", 503

    prompt = request.form.get('prompt', '')
    max_tokens = int(request.form.get('max_tokens', 256))
    
    if not prompt: return "Please provide a prompt.", 400

    generate_response(prompt, max_tokens)
    
    return redirect(url_for('main_page'))

@app.route('/save_session', methods=['POST'])
def save_current_session():
    """Saves the current chat history with a user-friendly, URL-safe name."""
    history = session.get('chat_history', [])
    if history:
        # Use existing session_id if it's already saved, otherwise create a new one
        session_id = session.get('session_id')
        if not session_id:
            first_prompt = history[0].replace('Instruct:', '').replace('\nOutput:', '').strip()
            safe_name = secure_filename(first_prompt[:30])
            session_id = f"{datetime.now().strftime('%Y%m%d-%H%M')}_{safe_name}"
        
        save_session(session_id, history)
        session['session_id'] = session_id # Ensure session_id is set
        
    return redirect(url_for('main_page'))

@app.route('/delete_session/<session_id>', methods=['GET'])
def delete_session_route(session_id):
    """Deletes a specific session."""
    delete_session(session_id)
    # If the deleted session was the active one, start a new chat
    if session.get('session_id') == session_id:
        return redirect(url_for('new_chat'))
    return redirect(url_for('main_page'))

@app.route('/settings', methods=['GET'])
def settings_page():
    """Displays the settings page."""
    return render_template("settings.html", prompt_template=PROMPT_TEMPLATE)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Updates the global prompt template."""
    global PROMPT_TEMPLATE
    new_template = request.form.get('prompt_template')
    if new_template:
        PROMPT_TEMPLATE = new_template
    return redirect(url_for('settings_page'))

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
