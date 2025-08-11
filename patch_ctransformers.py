#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTransformers Monkey-Patch Script for Python 3.6
=================================================

This script fixes the "cannot import name 'validate_repo_id'" error
by commenting out the unnecessary code in the ctransformers library.

This is a one-time fix. Run this script once to patch the library.
"""

import os
import sys
import site

def find_hub_py():
    """Find the hub.py file in the installed ctransformers library."""
    # Get all site-packages directories
    site_packages_dirs = site.getsitepackages()
    if hasattr(site, 'getusersitepackages'):
        site_packages_dirs.append(site.getusersitepackages())

    # Add common CDSW local path
    cdsw_local_path = os.path.expanduser("~/.local/lib/python{}.{}/site-packages".format(
        sys.version_info.major, sys.version_info.minor
    ))
    site_packages_dirs.insert(0, cdsw_local_path)

    for sp_dir in site_packages_dirs:
        hub_path = os.path.join(sp_dir, 'ctransformers', 'hub.py')
        if os.path.exists(hub_path):
            print("✅ Found hub.py at: {}".format(hub_path))
            return hub_path
    
    print("❌ ERROR: Could not find 'ctransformers/hub.py'.")
    print("Please ensure 'ctransformers' is installed (pip install -r requirements_py36.txt).")
    return None

def patch_file(file_path):
    """Comments out the problematic lines in the given file."""
    print("\n--- Starting Patch Process ---")
    
    try:
        # Read the original file content
        with open(file_path, 'r') as f:
            content = f.read()
            print("Read {} characters from file.".format(len(content)))

        # Define the lines to be patched
        line_to_patch_1 = "from huggingface_hub.utils import validate_repo_id, HFValidationError"
        replacement_1 = "# " + line_to_patch_1
        
        line_to_patch_2 = "validate_repo_id(path)"
        replacement_2 = "# " + line_to_patch_2

        # Check if the file is already patched
        if replacement_1 in content and replacement_2 in content:
            print("✅ File appears to be already patched. No changes needed.")
            return True

        # Perform the patching
        patched_content = content.replace(line_to_patch_1, replacement_1)
        patched_content = patched_content.replace(line_to_patch_2, replacement_2)

        if content == patched_content:
            print("⚠️ WARNING: Patching did not change the file content.")
            print("The problematic lines might have changed. Please check the file manually.")
            return False

        # Write the patched content back to the file
        with open(file_path, 'w') as f:
            f.write(patched_content)
            print("Wrote {} characters back to file.".format(len(patched_content)))

        print("✅ SUCCESS: The file has been patched successfully.")
        return True

    except Exception as e:
        print("❌ ERROR: An error occurred during the patching process.")
        print(str(e))
        return False

def main():
    """Main execution function."""
    print("--- CTransformers Patcher for Python 3.6 ---")
    hub_file = find_hub_py()
    
    if hub_file:
        patch_file(hub_file)
        print("\n--- Next Steps ---")
        print("The library is now patched. Please try running your main application script again:")
        print("python app_py36_compatible.py")

if __name__ == "__main__":
    main()
