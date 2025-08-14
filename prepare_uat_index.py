#!/usr/bin/env python3
"""
Prepare UAT Index with GraphRAG (v2.4.0)
=========================================

This script is a wrapper that constructs and executes the correct
`graphrag` command-line instruction to build the index.
"""

import os
import logging
import subprocess

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
INPUT_DIR = "sample_uat_documents" # Directory containing your source documents
OUTPUT_INDEX_DIR = "uat_graphrag_index"
LLM_MODEL_PATH = "path/to/your/model.gguf" # TODO: Update this path

# --- Main Indexing Logic ---
def main():
    """
    Main function to prepare the GraphRAG index.
    """
    logger.info("Starting GraphRAG UAT Index Preparation...")

    if not os.path.isdir(INPUT_DIR):
        logger.error(f"Input directory not found: {INPUT_DIR}")
        logger.info("Please create this directory and place your documents inside.")
        return

    os.makedirs(OUTPUT_INDEX_DIR, exist_ok=True)
    logger.info(f"Output index directory: {OUTPUT_INDEX_DIR}")

    # --- 1. Construct the GraphRAG command ---
    command = [
        "python3.10", "-m", "graphrag.cli",
        "--root", ".",
        "--data", INPUT_DIR,
        "--output", OUTPUT_INDEX_DIR,
        "--llm", "llama_cpp",
        "--llm-model", LLM_MODEL_PATH,
        "--embeddings-llm", "llama_cpp",
        "--embeddings-llm-model", LLM_MODEL_PATH,
        "index",
    ]

    # --- 2. Run the Indexing Command ---
    logger.info("Executing GraphRAG command:")
    logger.info(" ".join(command))
    
    try:
        subprocess.run(command, check=True)
        logger.info("Indexing process completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Indexing process failed: {e}")
        return

    logger.info(f"GraphRAG index has been saved to: {OUTPUT_INDEX_DIR}")

# --- Entry Point ---
if __name__ == '__main__':
    main()
