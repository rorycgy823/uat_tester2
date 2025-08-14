#!/usr/bin/env python3
"""
Simple Document Processor for UAT Generation
============================================

This script provides functions to read and extract text from various
document types (Word .docx, Excel .xlsx/.xls, and plain text .txt)
and convert them into a simple, unified text format suitable for
further processing by GraphRAG or other NLP tools.

This is a lightweight alternative to more complex processing pipelines.
"""

import os
from docx import Document
import pandas as pd
import logging

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_word_document(file_path):
    """
    Reads text from a Microsoft Word (.docx) file.
    
    Args:
        file_path (str): The path to the .docx file.
        
    Returns:
        str: The extracted text.
    """
    logger.info(f"Processing Word document: {file_path}")
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        logger.error(f"Failed to read Word document {file_path}: {e}")
        return ""

def read_excel_document(file_path):
    """
    Reads text from an Excel file (.xlsx or .xls).
    It reads all sheets and concatenates their content.
    
    Args:
        file_path (str): The path to the Excel file.
        
    Returns:
        str: The extracted text.
    """
    logger.info(f"Processing Excel document: {file_path}")
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file_path)
        full_text = []
        for sheet_name in excel_file.sheet_names:
            logger.info(f"  Reading sheet: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Convert the entire DataFrame to string
            full_text.append(f"--- Sheet: {sheet_name} ---")
            full_text.append(df.to_string(index=False))
            full_text.append("\n")
        return '\n'.join(full_text)
    except Exception as e:
        logger.error(f"Failed to read Excel document {file_path}: {e}")
        return ""

def read_text_document(file_path):
    """
    Reads text from a plain text file (.txt).
    
    Args:
        file_path (str): The path to the .txt file.
        
    Returns:
        str: The extracted text.
    """
    logger.info(f"Processing Text document: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read text document {file_path}: {e}")
        return ""

def process_document(file_path):
    """
    Automatically determines the file type and processes it accordingly.
    
    Args:
        file_path (str): The path to the document file.
        
    Returns:
        str: The extracted text, or an empty string if processing failed.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.docx':
        return read_word_document(file_path)
    elif ext in ['.xlsx', '.xls']:
        return read_excel_document(file_path)
    elif ext == '.txt':
        return read_text_document(file_path)
    else:
        logger.warning(f"Unsupported file type '{ext}' for file: {file_path}. Treating as plain text.")
        return read_text_document(file_path)

def process_directory(directory_path, output_file_path):
    """
    Processes all supported documents in a directory and saves the
    combined text to a single output file.
    
    Args:
        directory_path (str): Path to the directory containing documents.
        output_file_path (str): Path to the output .txt file.
    """
    logger.info(f"Starting to process directory: {directory_path}")
    
    if not os.path.isdir(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return

    combined_text = []
    
    # Walk through the directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            logger.info(f"Found file: {file_path}")
            
            # Process the document
            text = process_document(file_path)
            if text:
                combined_text.append(f"--- Document: {file_path} ---")
                combined_text.append(text)
                combined_text.append("\n" + "="*50 + "\n") # Separator

    # Write the combined text to the output file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(combined_text))
        logger.info(f"Combined text saved to: {output_file_path}")
    except Exception as e:
        logger.error(f"Failed to write output file {output_file_path}: {e}")


# --- Example Usage ---
if __name__ == '__main__':
    # Example 1: Process a single file
    # text = process_document('path/to/your/document.docx')
    # print(text[:500]) # Print first 500 characters

    # Example 2: Process a directory
    input_dir = "sample_uat_documents" # Change this to your directory
    output_file = "processed_uat_documents.txt"
    
    # Create a sample directory structure for demonstration
    # In a real scenario, you would point this to your actual documents
    os.makedirs(input_dir, exist_ok=True)
    
    # (You would place your actual .docx, .xlsx, .txt files in 'sample_uat_documents')
    
    process_directory(input_dir, output_file)
    print(f"Processing complete. Check '{output_file}' for results.")
