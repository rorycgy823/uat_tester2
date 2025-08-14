#!/bin/bash

# Script to install GraphRAG and its dependencies for the UAT Generator
# This script is designed to work within the CDSW Python 3.10 environment.

set -e # Exit immediately if a command exits with a non-zero status.

echo "Starting GraphRAG installation process..."

# --- 1. Ensure we are using the correct Python environment ---
# This script assumes it's run in a CDSW session where Python 3.10 is the default
# or where a virtual environment has been activated.
PYTHON_CMD="python3.10"
PIP_CMD="pip3"

echo "Using Python: $($PYTHON_CMD --version)"
echo "Using Pip: $($PIP_CMD --version)"

# --- 2. Install/Upgrade Pip, Setuptools, and Wheel (Good Practice) ---
echo "Upgrading pip, setuptools, and wheel..."
$PIP_CMD install --upgrade pip setuptools wheel

# --- 3. Install Microsoft GraphRAG and other dependencies ---
echo "Installing GraphRAG and dependencies from graphrag_requirements.txt..."
$PIP_CMD install -r graphrag_requirements.txt

# --- 4. Post-Installation Message ---
echo "----------------------------------------"
echo "GraphRAG installation completed successfully!"
echo "You can now proceed with setting up your UAT generation pipeline."
echo "----------------------------------------"
