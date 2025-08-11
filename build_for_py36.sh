#!/bin/bash

# =================================================================
# FINAL Definitive Build Script for Python 3.6
# =================================================================
# This script is the definitive solution. It explicitly uses python3.6
# for all operations and forces a clean rebuild of ctransformers
# to resolve all previous environment and build issues.
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting Definitive CTransformers Build for Python 3.6 ---"

# --- Step 1: Verify Python 3.6 is available ---
if ! command -v python3.6 &> /dev/null; then
    echo "ERROR: python3.6 command not found. This script requires it."
    exit 1
fi
echo "Using Python 3.6 interpreter at: $(which python3.6)"


# --- Step 2: Uninstall Existing CTransformers using python3.6-pip ---
echo "Uninstalling any existing ctransformers package from Python 3.6 environment..."
python3.6 -m pip uninstall -y ctransformers || echo "ctransformers was not previously installed in Python 3.6 env. Continuing."


# --- Step 3: Install/Upgrade Build Dependencies using python3.6-pip ---
# We ensure the build tools are available for the Python 3.6 environment.
echo "Installing/upgrading build dependencies for Python 3.6..."
python3.6 -m pip install --upgrade --prefer-binary "cmake>=3.18" "scikit-build>=0.13" "ninja"


# --- Step 4: Set Environment Variables for Build ---
echo "Setting environment variables for compilation..."
export CMAKE_ARGS="-DGGML_BUILD_TESTS=OFF"


# --- Step 5: Force Install CTransformers from Source using python3.6-pip ---
# This is the most critical step.
# --force-reinstall and --ignore-installed will ensure the build runs
# even if pip thinks the package is already there.
# We explicitly use 'python3.6 -m pip' to guarantee the correct environment.
CT_VERSION="ctransformers==0.2.24"
echo "Force-installing ${CT_VERSION} from source for Python 3.6. This may take several minutes..."

python3.6 -m pip install \
    --force-reinstall \
    --ignore-installed \
    --no-binary ctransformers \
    --verbose \
    "${CT_VERSION}"


# --- Step 6: Verification using python3.6 ---
echo "--- Verification Step ---"
echo "Verifying the new installation in the Python 3.6 environment..."

# This command will now definitively check the Python 3.6 environment.
python3.6 -c "from ctransformers import AutoModelForCausalLM; print('✅ SUCCESS: ctransformers library imported successfully in Python 3.6.')"

echo "------------------------------------------------"
echo "✅ DEFINITIVE BUILD COMPLETE."
echo "All known issues should now be resolved."
echo "Please run your application using the python3.6 command:"
echo "python3.6 app_py36_compatible.py"
echo "------------------------------------------------"
