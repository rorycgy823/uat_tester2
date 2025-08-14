#!/usr/bin/env python3
"""
Query UAT Index with GraphRAG (v2.4.0)
======================================

This script is a wrapper that constructs and executes the correct
`graphrag` command-line instruction to query the index.
"""

import os
import logging
import subprocess
import sys

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
INDEX_DIR = "uat_graphrag_index"
LLM_MODEL_PATH = "path/to/your/model.gguf" # TODO: Update this path

# --- Query Logic ---
def main(user_query):
    """
    Main function to query the GraphRAG index.
    """
    logger.info("Starting GraphRAG UAT Query...")

    if not os.path.isdir(INDEX_DIR):
        logger.error(f"Index directory not found: {INDEX_DIR}")
        return "Error: Index not found. Please run prepare_uat_index.py first."

    # --- 1. Construct the GraphRAG command ---
    command = [
        "python3.10", "-m", "graphrag.cli",
        "--root", ".",
        "--data", INDEX_DIR, # For querying, --data points to the index
        "--llm", "llama_cpp",
        "--llm-model", LLM_MODEL_PATH,
        "--embeddings-llm", "llama_cpp",
        "--embeddings-llm-model", LLM_MODEL_PATH,
        "query",
        f'"{user_query}"', # Pass the query as an argument
    ]

    # --- 2. Run the Query Command ---
    logger.info("Executing GraphRAG command:")
    logger.info(" ".join(command))
    
    try:
        result = subprocess.run(
            " ".join(command), # Run as a single string because of the quoted query
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Query process completed successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Query process failed: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return f"Error during query: {e.stderr}"

# --- Entry Point ---
if __name__ == '__main__':
    # The query is passed as a command-line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        query_result = main(query)
        if query_result:
            print(query_result)
    else:
        print("Usage: python query_uat_index.py <your query>")
