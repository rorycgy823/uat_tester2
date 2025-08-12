#!/usr/bin/env python3
"""
Conversational Phi-2 GGUF Model Server
=======================================

A Flask application with a chat UI to interact with a GGUF model.
This version supports conversation history and adjustable parameters.
"""

import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.serving import ThreadedWSGIServer
import socket

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variable to hold the model and chat history
llm = None
chat_history = []

def load_model():
    """
    Finds and loads the GGUF model using llama-cpp-python.
    """
    global llm
    try:
        from llama_cpp import Llama
    except ImportError:
        logger.error("FATAL: llama-cpp-python library not found.")
        logger.error("Please build and install it using the build_llama_cpp.sh script.")
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

# --- Flask Application ---
app = Flask(__name__)

# --- Main Chat Logic ---
def generate_response(prompt, max_tokens):
    """
    Generates a response from the model, including chat history.
    """
    global chat_history
    
    # Add the new user prompt to the history
    chat_history.append(f"Instruct: {prompt}\nOutput:")
    
    # Create the full prompt by joining the history
    full_prompt = "\n".join(chat_history)
    
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
    
    # Add the model's answer to the history
    chat_history.append(answer)
    
    return answer

# --- Web UI Routes ---
@app.route('/', methods=['GET'])
def main_page():
    """Serves the main chat UI."""
    return render_template("index.html", history=chat_history)

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handles a new chat message from the user."""
    if llm is None:
        return "Model is not loaded.", 503

    prompt = request.form.get('prompt', '')
    max_tokens = int(request.form.get('max_tokens', 256))
    
    if not prompt:
        return "Please provide a prompt.", 400

    generate_response(prompt, max_tokens)
    
    return redirect(url_for('main_page'))

@app.route('/new_chat', methods=['GET'])
def new_chat():
    """Clears the chat history and starts a new conversation."""
    global chat_history
    chat_history = []
    return redirect(url_for('main_page'))

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
