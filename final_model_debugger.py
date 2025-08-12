#!/usr/bin/env python3
"""
Final Model Debugger for CTransformers
========================================

This script is a diagnostic tool to solve the "Failed to create LLM"
RuntimeError. It systematically tries different `model_type` values
to find the correct one for your GGUF file.

Instructions:
1. Make sure your dependencies are installed for Python 3.10.
2. Place your 'phi-2.Q4_K_M.gguf' model file in the project directory.
3. Run this script from your CDSW terminal:
   python3.10 final_model_debugger.py
"""

import os
import logging
import sys

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_model_path():
    """Finds the GGUF model file."""
    model_filename = "phi-2.Q4_K_M.gguf"
    possible_paths = [
        model_filename,
        f"/home/cdsw/{model_filename}",
        f"/home/cdsw/models/{model_filename}",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found GGUF model at: {path}")
            return os.path.abspath(path)
            
    logger.error(f"FATAL: Could not find the model file '{model_filename}'.")
    return None

def debug_model_loading(model_path):
    """
    Tries to load the model with different `model_type` values.
    """
    try:
        from ctransformers import AutoModelForCausalLM
    except ImportError:
        logger.error("FATAL: ctransformers library not found.")
        logger.error("Please install dependencies: python3.10 -m pip install -r requirements_py310.txt")
        return

    # A comprehensive list of potential model types for GGUF files.
    # Phi-2 is based on the 'gpt_neox' architecture.
    model_types_to_try = [
        'phi',
        'gpt_neox',
        'gpt2',
        'llama',
        'starcoder',
        'mpt',
        'gptj',
        'dolly-v2',
        'replit',
    ]

    logger.info(f"--- Starting Debugging for Model: {model_path} ---")

    for model_type in model_types_to_try:
        logger.info(f"\n>>> ATTENTION: Attempting to load with model_type = '{model_type}'...")
        try:
            llm = AutoModelForCausalLM.from_pretrained(
                model_path,
                model_type=model_type,
                gpu_layers=0,
                context_length=2048
            )
            
            logger.info("✅✅✅ SUCCESS! ✅✅✅")
            logger.info(f"The model loaded successfully with model_type = '{model_type}'.")
            logger.info("Please update your `app_py310.py` script to use this model_type.")
            
            # Optional: Run a quick test generation
            logger.info("Running a quick test generation...")
            test_prompt = "What is the capital of France?"
            response = llm(test_prompt, max_new_tokens=10)
            logger.info(f"Test Prompt: {test_prompt}")
            logger.info(f"Test Response: {response}")
            
            return model_type

        except Exception as e:
            logger.error(f"--- FAILED with model_type = '{model_type}' ---")
            logger.error(f"Error details: {e}")
            logger.error("-" * 50)

    return None

if __name__ == '__main__':
    model_path = find_model_path()
    
    if not model_path:
        sys.exit(1)
        
    successful_type = debug_model_loading(model_path)
    
    print("\n" + "="*60)
    if successful_type:
        print(f"✅ DEBUGGING COMPLETE: The correct model_type is '{successful_type}'.")
        print("Please update this line in your `app_py310.py` script:")
        print(f"model_type='{successful_type}',")
    else:
        print("❌ DEBUGGING FAILED: None of the tested model_types were successful.")
        print("This suggests the issue may be with the GGUF model file itself.")
        print("Please try the following:")
        print("1. Re-download the 'phi-2.Q4_K_M.gguf' file to ensure it is not corrupted.")
        print("2. Check if there is a newer version of the `ctransformers` library that might support this GGUF format.")
    print("="*60)
