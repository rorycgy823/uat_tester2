#!/usr/bin/env python3
"""
GraphRAG Installation Debugger
==============================

This script is designed to be run in your CDSW Python 3.10 environment
to diagnose the installation and import issues with the GraphRAG library.

Please run this script and provide the full output.
"""

import sys
import subprocess
import pkg_resources

def run_command(command):
    """Runs a shell command and returns its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error running command: {command}\n{e.stderr}"

def check_python_version():
    """Checks the current Python version."""
    print("--- 1. Checking Python Version ---")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print("-" * 30 + "\n")

def check_installed_packages():
    """Lists all installed packages and their versions."""
    print("--- 2. Checking Installed Packages (pip list) ---")
    packages = run_command("pip list")
    print(packages)
    print("-" * 30 + "\n")

def check_graphrag_version():
    """Checks the installed version of the graphrag library."""
    print("--- 3. Checking GraphRAG Version ---")
    try:
        import graphrag
        print(f"Successfully imported 'graphrag'")
        print(f"GraphRAG version: {graphrag.__version__}")
    except ImportError as e:
        print(f"Failed to import 'graphrag': {e}")
    except Exception as e:
        print(f"An unexpected error occurred while importing 'graphrag': {e}")
    print("-" * 30 + "\n")

def check_graphrag_index_import():
    """Attempts to import from graphrag.index to replicate the error."""
    print("--- 4. Attempting to Import from graphrag.index ---")
    try:
        # We are trying to see what is available in the 'index' module
        import graphrag.index
        print("Successfully imported 'graphrag.index'")
        
        # Let's see what's inside
        print("\nContents of 'graphrag.index':")
        print(dir(graphrag.index))
        
        # Now, let's try the specific import that failed
        print("\nAttempting to import 'create_indexer'...")
        from graphrag.index import create_indexer
        print("Successfully imported 'create_indexer' from 'graphrag.index'")
        
    except ImportError as e:
        print(f"Failed to import from 'graphrag.index': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("-" * 30 + "\n")

if __name__ == '__main__':
    print("Starting GraphRAG Installation Debugger...")
    print("=" * 50)
    
    check_python_version()
    check_installed_packages()
    check_graphrag_version()
    check_graphrag_index_import()
    
    print("=" * 50)
    print("Debugging script finished.")
    print("Please copy and paste the entire output of this script for further analysis.")
