#!/usr/bin/env python3
"""
Simple Phi-2 GGUF Model Server using llama-cpp-python
======================================================

A minimal Flask application to load a GGUF model and serve it.
This script is designed for Python 3.10 and uses the robust
llama-cpp-python library.

Instructions:
1. Build and install llama-cpp-python using the build_llama_cpp.sh script.
2. Install other requirements:
   python3.10 -m pip install -r requirements_llama.txt
3. Place your 'phi-2.Q4_K_M.gguf' model file in the project directory.
4. Run as a CDSW Application, pointing to this script.
"""

import os
import logging
from flask import Flask, request, jsonify

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variable to hold the model
llm = None

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

    # Find the model file
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

    # Load the model using llama-cpp-python syntax
    try:
        logger.info("Loading Phi-2 GGUF model with llama-cpp-python...")
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,      # Context length
            n_threads=4,     # Number of CPU threads to use
            n_gpu_layers=0   # Ensure CPU-only operation
        )
        logger.info("✅ Model loaded successfully!")
        return True
    except Exception as e:
        logger.error("FATAL: Failed to load the model with llama-cpp-python.")
        logger.error(f"Error details: {e}")
        return False

# --- Flask Application ---
app = Flask(__name__)

# --- HTML Templates ---
# Simple CSS for better presentation
STYLE_SHEET = """
<style>
    body { font-family: sans-serif; margin: 2em; background-color: #f4f4f9; color: #333; }
    h1 { color: #4a4a8a; }
    .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    textarea { width: 95%; padding: 10px; border-radius: 4px; border: 1px solid #ddd; font-size: 1em; }
    input[type=submit] { background-color: #4a4a8a; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 1em; }
    .prompt, .answer { background-color: #f9f9f9; border-left: 5px solid #4a4a8a; padding: 10px; margin-top: 20px; white-space: pre-wrap; }
    .answer { border-left-color: #5cb85c; }
    a { color: #4a4a8a; text-decoration: none; }
</style>
"""

MAIN_PAGE_HTML = STYLE_SHEET + """
<div class="container">
    <h1>Ask Phi-2 a Question</h1>
    <form action="/ask" method="post">
        <textarea name="prompt" rows="10" placeholder="Type your question here..."></textarea>
        <br><br>
        <input type="submit" value="Ask Model">
    </form>
</div>
"""

ANSWER_PAGE_HTML = STYLE_SHEET + """
<div class="container">
    <h1>Result</h1>
    <div class="prompt">
        <h2>Your Question:</h2>
        <p>{prompt}</p>
    </div>
    <div class="answer">
        <h2>Model's Answer:</h2>
        <p>{answer}</p>
    </div>
    <br>
    <a href="/">Ask another question</a>
</div>
"""

# --- Web UI Routes ---
@app.route('/', methods=['GET'])
def main_page():
    """Serves the main HTML page with the question form."""
    return MAIN_PAGE_HTML

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handles the form submission and displays the answer."""
    if llm is None:
        return "Model is not loaded.", 503

    prompt = request.form.get('prompt', '')
    if not prompt:
        return "Please provide a prompt.", 400

    logger.info(f"Generating text for UI prompt: '{prompt[:80]}'...")
    
    # Using a standard instruction format for better responses
    full_prompt = f"Instruct: {prompt}\nOutput:"
    
    output = llm(
        full_prompt,
        max_tokens=512,
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.1,
        stop=["</end>", "[END]", "Instruct:"]
    )
    answer = output["choices"][0]["text"]
    
    logger.info("Generation complete.")
    
    return ANSWER_PAGE_HTML.format(prompt=prompt, answer=answer)


@app.route('/generate', methods=['POST'])
def generate_text():
    """
    The main generation endpoint.
    """
    if llm is None:
        return jsonify({"error": "Model is not loaded or failed to load."}), 503

    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Request must include a 'prompt'."}), 400
            
        logger.info(f"Generating text for prompt: '{prompt[:80]}'...")
        
        # Generate text using the llama-cpp-python model
        output = llm(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["</end>", "[END]"]
        )
        
        generated_text = output["choices"][0]["text"]
        
        logger.info("Generation complete.")
        
        return jsonify({
            "prompt": prompt,
            "generated_text": generated_text
        })

    except Exception as e:
        logger.error(f"An error occurred during generation: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """A simple health check endpoint."""
    if llm is not None:
        return jsonify({"status": "healthy", "model": "Phi-2 GGUF Loaded (llama-cpp)"}), 200
    else:
        return jsonify({"status": "unhealthy", "model": "Model Not Loaded"}), 500

if __name__ == '__main__':
    # Load the model on startup
    model_loaded = load_model()
    
    if model_loaded:
        # Get CDSW-provided host and port
        host = os.environ.get('CDSW_IP_ADDRESS', '127.0.0.1')
        port = int(os.environ.get('CDSW_APP_PORT', 8080))
        
        logger.info(f"Starting Flask server on {host}:{port}")
        app.run(host=host, port=port, debug=False)
    else:
        logger.error("Application cannot start because the model failed to load.")
        exit(1)
