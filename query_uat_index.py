#!/usr/bin/env python3
"""
Query UAT Index with GraphRAG
=============================

This script demonstrates how to load a pre-built GraphRAG index
and use it to answer queries, which is the core of the UAT generation.

This version uses the updated GraphRAG API.
"""

import os
import logging
import asyncio
from graphrag.query.cli import run_query_with_config
from graphrag.config import create_graphrag_config

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
INDEX_DIR = "uat_graphrag_index"
LLM_MODEL_PATH = "path/to/your/model.gguf" # TODO: Update this path

# --- Query Logic ---
async def main(user_query):
    """
    Main async function to query the GraphRAG index.
    """
    logger.info("Starting GraphRAG UAT Query...")

    if not os.path.exists(INDEX_DIR):
        logger.error(f"Index directory not found: {INDEX_DIR}")
        logger.info("Please run 'prepare_uat_index.py' first.")
        return

    # --- 1. Create GraphRAG Configuration ---
    # This configuration points to the existing index and specifies the query LLM.
    config = create_graphrag_config(
        root_dir=os.getcwd(),
        llm={
            "type": "llama_cpp",
            "model": LLM_MODEL_PATH,
            "n_ctx": 4096,
        },
        embeddings={
            "type": "llama_cpp",
            "model": LLM_MODEL_PATH,
        },
    )

    # --- 2. Run the Query Pipeline ---
    logger.info(f"Processing user query: {user_query}")
    try:
        result = await run_query_with_config(
            config,
            data_dir=INDEX_DIR,
            query=user_query,
            # You can specify different query types here, e.g., "global" or "local"
            # method="global", 
        )
        logger.info("Query process completed successfully.")
        return result
    except Exception as e:
        logger.error(f"Query process failed: {e}")
        return None

# --- Entry Point ---
if __name__ == '__main__':
    sample_query = "Generate a UAT test case for user story: As a user, I want to reset my password."
    
    # Run the async main function
    query_result = asyncio.run(main(sample_query))
    
    if query_result:
        print("\n--- UAT Generation Result ---")
        print(query_result)
        print("-----------------------------\n")
