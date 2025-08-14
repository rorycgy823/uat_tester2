#!/usr/bin/env python3
"""
GraphRAG API Inspector
======================

This script is designed to be run in your CDSW Python 3.10 environment
to inspect the available modules and functions within the GraphRAG library.

Please run this script and provide the full output.
"""

import sys
import pkg_resources

def inspect_module(module_name):
    """Inspects a module and prints its contents."""
    print(f"--- Inspecting Module: {module_name} ---")
    try:
        module = __import__(module_name, fromlist=[''])
        print(f"Successfully imported '{module_name}'")
        
        print(f"\nContents of '{module_name}':")
        print(dir(module))
        
    except ImportError as e:
        print(f"Failed to import '{module_name}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    print("-" * 30 + "\n")

if __name__ == '__main__':
    print("Starting GraphRAG API Inspector...")
    print("=" * 50)
    
    inspect_module("graphrag")
    inspect_module("graphrag.index")
    inspect_module("graphrag.index.operations")
    inspect_module("graphrag.query")
    
    print("=" * 50)
    print("Inspection script finished.")
    print("Please copy and paste the entire output of this script for further analysis.")
