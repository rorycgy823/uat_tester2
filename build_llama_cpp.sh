#!/bin/bash

# =================================================================
# Build llama-cpp-python for Legacy CPU on Python 3.10
# =================================================================
# This script builds the llama-cpp-python library from source with
# CPU-specific optimizations disabled to ensure compatibility with
# older hardware and prevent Segmentation Faults (Exit Code 139).
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting llama-cpp-python Build for Legacy CPU ---"

# --- Step 1: Verify Python 3.10 is available ---
if ! command -v python3.10 &> /dev/null; then
    echo "ERROR: python3.10 command not found. This script requires it."
    exit 1
fi
echo "Using Python 3.10 interpreter at: $(which python3.10)"


# --- Step 2: Uninstall Existing llama-cpp-python ---
echo "Uninstalling any existing llama-cpp-python package..."
python3.10 -m pip uninstall -y llama-cpp-python || echo "llama-cpp-python was not previously installed. Continuing."


# --- Step 3: Install/Upgrade Build Dependencies ---
echo "Installing/upgrading build dependencies (cmake, ninja)..."
python3.10 -m pip install --upgrade --prefer-binary "cmake>=3.18" "ninja"


# --- Step 4: Set Environment Variables for Legacy CPU Build ---
# This is the CRITICAL step. We tell the compiler to build a generic
# library without modern CPU instructions like AVX, AVX2, or FMA.
echo "Setting environment variables for legacy CPU compilation..."
export CMAKE_ARGS="-DLLAMA_AVX=OFF -DLLAMA_AVX2=OFF -DLLAMA_FMA=OFF"
echo "CMake arguments set to: ${CMAKE_ARGS}"


# --- Step 5: Force Install llama-cpp-python from Source ---
# This forces a new compilation with the legacy CPU flags.
LLAMA_VERSION="llama-cpp-python==0.2.20"
echo "Force-installing ${LLAMA_VERSION} from source. This may take several minutes..."

python3.10 -m pip install \
    --force-reinstall \
    --ignore-installed \
    --no-binary llama-cpp-python \
    --verbose \
    "${LLAMA_VERSION}"


# --- Step 6: Verification ---
echo "--- Verification Step ---"
echo "Verifying the new legacy-compatible installation..."
python3.10 -c "from llama_cpp import Llama; print('✅ SUCCESS: llama-cpp-python library imported successfully.')"

echo "------------------------------------------------"
echo "✅ LEGACY BUILD FOR LLAMA-CPP-PYTHON COMPLETE."
echo "The model loading error should now be resolved."
echo "You can now create your application script using this library."
echo "------------------------------------------------"
