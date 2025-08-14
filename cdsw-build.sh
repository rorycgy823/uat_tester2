#!/bin/bash

# CDSW Build Script for the Conversational AI and UAT Generation App
# =================================================================

# This script automates the entire setup process for the application.
# It should be run once in your CDSW project's terminal to set up
# the environment, process documents, and build the GraphRAG index.

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting CDSW Build Process ---"

# --- 1. Install Python Dependencies ---
echo "\n>>> Step 1: Installing Python dependencies..."
# Install dependencies for the main chat application
pip3 install -r requirements_llama.txt
# Install dependencies for the GraphRAG UAT generator
pip3 install -r graphrag_requirements.txt
echo "Python dependencies installed successfully."

# --- 2. Process Source Documents ---
echo "\n>>> Step 2: Processing source documents for UAT generation..."
# This script needs to be configured to point to your document directory.
# For now, it will create a sample directory if one doesn't exist.
if [ ! -d "sample_uat_documents" ]; then
    echo "Creating sample directory 'sample_uat_documents'..."
    mkdir sample_uat_documents
    echo "Please place your .docx, .xlsx, and .txt files in this directory."
fi
python3.10 simple_document_processor.py
echo "Document processing complete. Output: processed_uat_documents.txt"

# --- 3. Build the GraphRAG Index ---
echo "\n>>> Step 3: Building the GraphRAG index..."
echo "This step may take a significant amount of time depending on the number of documents and the LLM."
# NOTE: You must update 'prepare_uat_index.py' with the correct path to your LLM model.
python3.10 prepare_uat_index.py
echo "GraphRAG index built successfully in 'uat_graphrag_index' directory."

# --- 4. Final Setup Complete ---
echo "\n--- CDSW Build Process Finished ---"
echo "The application is now fully set up."
echo "You can now run the main application by executing:"
echo "python3.10 app_chat.py"
echo "-----------------------------------"
