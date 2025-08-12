#!/bin/bash

# =================================================================
# Build Script for Legacy CPU on Python 3.10
# =================================================================
# This script resolves the "failed to load model" error, which is
# likely a Segmentation Fault (Exit Code 139), by compiling
# ctransformers for Python 3.10 with modern CPU instruction sets
# explicitly disabled.
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting CTransformers Build for Legacy CPU on Python 3.10 ---"

# --- Step 1: Verify Python 3.10 is available ---
if ! command -v python3.10 &> /dev/null; then
    echo "ERROR: python3.10 command not found. This script requires it."
    exit 1
fi
echo "Using Python 3.10 interpreter at: $(which python3.10)"


# --- Step 2: Uninstall Existing CTransformers ---
echo "Uninstalling any existing ctransformers package for a clean build..."
python3.10 -m pip uninstall -y ctransformers || echo "ctransformers was not previously installed. Continuing."


# --- Step 3: Install/Upgrade Build Dependencies ---
echo "Installing/upgrading build dependencies for Python 3.10..."
python3.10 -m pip install --upgrade --prefer-binary "cmake>=3.18" "scikit-build>=0.13" "ninja"


# --- Step 4: Set Environment Variables for Legacy CPU Build ---
# This is the CRITICAL step to prevent segmentation faults.
# We are telling the compiler NOT to use modern instruction sets.
echo "Setting environment variables for legacy CPU compilation..."
export CMAKE_ARGS="-DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF"
echo "CMake arguments set to: ${CMAKE_ARGS}"


# --- Step 5: Force Install CTransformers from Source ---
# This forces a new compilation with the legacy CPU flags for Python 3.10.
CT_VERSION="ctransformers==0.2.27"
echo "Force-installing ${CT_VERSION} from source. This may take several minutes..."

python3.10 -m pip install \
    --force-reinstall \
    --ignore-installed \
    --no-binary ctransformers \
    --verbose \
    "${CT_VERSION}"


# --- Step 6: Verification ---
echo "--- Verification Step ---"
echo "Verifying the new legacy-compatible installation..."
python3.10 -c "from ctransformers import AutoModelForCausalLM; print('✅ SUCCESS: Legacy-compatible ctransformers library imported successfully.')"

echo "------------------------------------------------"
echo "✅ LEGACY BUILD FOR PYTHON 3.10 COMPLETE."
echo "The model loading error should now be resolved."
echo "Please run your application using the python3.10 command:"
echo "python3.10 app_py310.py"
echo "------------------------------------------------"
