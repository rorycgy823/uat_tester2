#!/usr/bin/env python3
"""
Prepare UAT Index with GraphRAG
===============================

This script is the entry point for preparing the GraphRAG index
using your UAT documents (user stories, test cases, YAML files).

This version uses the updated GraphRAG API.
"""

import os
import logging
import asyncio
from graphrag.config import create_graphrag_config
from graphrag.index.operations import run_pipeline_with_config

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
INPUT_FILE_PATH = "processed_uat_documents.txt"
OUTPUT_INDEX_DIR = "uat_graphrag_index"
LLM_MODEL_PATH = "path/to/your/model.gguf" # TODO: Update this path

# --- Main Indexing Logic ---
async def main():
    """
    Main async function to prepare the GraphRAG index.
    """
    logger.info("Starting GraphRAG UAT Index Preparation...")

    if not os.path.exists(INPUT_FILE_PATH):
        logger.error(f"Input file not found: {INPUT_FILE_PATH}")
        logger.info("Please run 'simple_document_processor.py' first.")
        return

    os.makedirs(OUTPUT_INDEX_DIR, exist_ok=True)
    logger.info(f"Output index directory: {OUTPUT_INDEX_DIR}")

    # --- 1. Create GraphRAG Configuration ---
    # This is a simplified configuration. You can customize this further.
    config = create_graphrag_config(
        root_dir=os.getcwd(),
        output_dir=OUTPUT_INDEX_DIR,
        llm={
            "type": "llama_cpp",
            "model": LLM_MODEL_PATH,
            "n_ctx": 4096,
        },
        embeddings={
            "type": "llama_cpp",
            "model": LLM_MODEL_PATH,
        },
        chunks={
            "size": 1000,
            "overlap": 100,
        },
        input={
            "type": "text",
            "files": [INPUT_FILE_PATH],
        },
    )

    # --- 2. Run the Indexing Pipeline ---
    logger.info("Starting indexing process... (This may take a while)")
    try:
        await run_pipeline_with_config(config)
        logger.info("Indexing process completed successfully.")
    except Exception as e:
        logger.error(f"Indexing process failed: {e}")
        return

    logger.info(f"GraphRAG index has been saved to: {OUTPUT_INDEX_DIR}")

# --- Entry Point ---
if __name__ == '__main__':
    asyncio.run(main())
