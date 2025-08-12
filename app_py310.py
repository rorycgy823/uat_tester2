#!/usr/bin/env python3
"""
Simple Phi-2 GGUF Model Server for CDSW (Python 3.10)
=====================================================

A minimal Flask application to load a GGUF model and serve it.
This script is designed for a modern Python 3.10 environment.

Instructions:
1. Install requirements:
   python3.10 -m pip install -r requirements_py310.txt
2. Place your 'phi-2.Q4_K_M.gguf' model file in the project directory.
3. Run as a CDSW Application, pointing to this script.
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
    Finds and loads the GGUF model into the global 'llm' variable.
    """
    global llm
    
    try:
        from ctransformers import AutoModelForCausalLM
    except ImportError:
        logger.error("FATAL: ctransformers library not found.")
        logger.error("Please install dependencies: python3.10 -m pip install -r requirements_py310.txt")
        return False

    # Find the model file
    model_filename = "phi-2.Q4_K_M.gguf"
    model_path = None
    
    # Check common paths in CDSW
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

    # Load the model
    try:
        logger.info("Loading Phi-2 GGUF model... This may take a moment.")
        # With modern ctransformers, we can be more direct with the model_type
        llm = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type='phi',
            gpu_layers=0,       # Ensure CPU-only operation
            context_length=2048
        )
        logger.info("✅ Model loaded successfully!")
        return True
    except Exception as e:
        logger.error("FATAL: Failed to load the model.")
        logger.error(f"Error details: {e}")
        # This could still be a GLIBC or CPU instruction issue if the error persists.
        return False

# --- Flask Application ---
app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_text():
    """
    The main generation endpoint.
    Accepts a JSON request with a 'prompt' key.
    """
    if llm is None:
        return jsonify({"error": "Model is not loaded or failed to load."}), 503

    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "Request must include a 'prompt'."}), 400
            
        logger.info(f"Generating text for prompt: '{prompt[:80]}'...")
        
        # Generate text using the model
        generated_text = llm(
            prompt,
            max_new_tokens=256,
            temperature=0.7,
            repetition_penalty=1.1
        )
        
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
        return jsonify({"status": "healthy", "model": "Phi-2 GGUF Loaded"}), 200
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
