#!/bin/bash

# =================================================================
# FINAL DEFINITIVE SOLUTION SCRIPT
# =================================================================
# This script combines all successful steps into one process:
# 1. Builds ctransformers from source to solve GLIBC/build issues.
# 2. Force-installs the correct dependency versions from requirements.
# 3. Patches the final import error in the library.
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting Final Solution Process for Python 3.6 ---"

# --- Step 1: Build and Install ctransformers from Source ---
# This uses the logic from our successful build_for_py36.sh script.
echo "STEP 1: Building ctransformers from source..."
chmod +x build_for_py36.sh
./build_for_py36.sh
echo "Build process completed."


# --- Step 2: Force-Install Correct Dependencies ---
# This is a CRITICAL step. The build process may have installed incorrect
# dependency versions. This command overwrites them with the correct
# versions from our requirements_py36.txt file.
echo -e "\nSTEP 2: Force-installing correct dependencies from requirements_py36.txt..."
python3.6 -m pip install --ignore-installed -r requirements_py36.txt
echo "Dependencies have been aligned."


# --- Step 3: Patch the ctransformers Library ---
# Now that the library is built and dependencies are correct, we
# apply the patch to fix the final 'validate_repo_id' import error.
echo -e "\nSTEP 3: Patching the ctransformers library..."
chmod +x patch_ctransformers.py
python3.6 patch_ctransformers.py
echo "Patch applied successfully."


# --- Step 4: Final Verification ---
echo -e "\nSTEP 4: Final Verification..."
# This command will now check the fully built, dependency-corrected,
# and patched library in the Python 3.6 environment.
python3.6 -c "from ctransformers import AutoModelForCausalLM; print('✅ SUCCESS: ctransformers can be imported successfully!')"

echo "------------------------------------------------"
echo "✅ FINAL SOLUTION COMPLETE."
echo "All issues should now be resolved."
echo "You can now run your application using the python3.6 command:"
echo "python3.6 app_py36_compatible.py"
echo "------------------------------------------------"
