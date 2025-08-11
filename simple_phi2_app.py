#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Phi-2 GGUF Model Server for CDSW (Python 3.6)
=====================================================

This is a minimal Flask application to load a GGUF model and serve it
at a single endpoint. It is designed for CDSW v1.10 and Python 3.6.

Instructions:
1. Ensure ctransformers is built correctly using the build script.
2. Install requirements:
   pip install -r simple_requirements.txt
3. Place your 'phi-2.Q4_K_M.gguf' model file in the same directory.
4. Run as a CDSW Application, pointing to this script.
"""

import os
import logging
from flask import Flask, request, jsonify

# --- Basic Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tell transformers library to be quiet on startup
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Global variable to hold the model
llm = None

def load_model():
    """
    Finds and loads the GGUF model into the global 'llm' variable.
    """
    global llm
    
    # Check if ctransformers is installed
    try:
        from ctransformers import AutoModelForCausalLM
    except ImportError:
        logger.error("FATAL: ctransformers library not found.")
        logger.error("Please build and install it using the build_for_py36.sh script.")
        return False

    # Find the model file in common CDSW locations
    model_filename = "phi-2.Q4_K_M.gguf"
    model_paths = [
        model_filename,
        os.path.join("/home/cdsw/", model_filename),
        os.path.join("/home/cdsw/models/", model_filename),
    ]
    
    model_path = None
    for path in model_paths:
        if os.path.exists(path):
            model_path = path
            logger.info("Found GGUF model at: {}".format(model_path))
            break
            
    if not model_path:
        logger.error("FATAL: Could not find the model file '{}'.".format(model_filename))
        return False

    # Load the model
    try:
        logger.info("Loading Phi-2 GGUF model... This may take a moment.")
        llm = AutoModelForCausalLM.from_pretrained(
            model_path,
            model_type='gpt2',  # 'gpt2' is a safe and compatible type for Phi-2
            gpu_layers=0,       # Ensure CPU-only operation
            context_length=2048
        )
        logger.info("✅ Model loaded successfully!")
        return True
    except Exception as e:
        logger.error("FATAL: Failed to load the model.")
        logger.error("The ctransformers library might be built incorrectly.")
        logger.error("Error details: {}".format(e))
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
            
        logger.info("Generating text for prompt: '{}'...".format(prompt[:80]))
        
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
        logger.error("An error occurred during generation: {}".format(e))
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
        
        logger.info("Starting Flask server on {}:{}".format(host, port))
        app.run(host=host, port=port, debug=False)
    else:
        logger.error("Application cannot start because the model failed to load.")
        # Exit with a non-zero code to indicate failure to CDSW
        exit(1)
