#!/bin/bash

# =================================================================
# Build CTransformers from Source for GLIBC Compatibility
# =================================================================
# This script resolves the 'GLIBC_2.29 not found' error by
# uninstalling the pre-compiled ctransformers library and
# reinstalling it by compiling it from source inside the
# CDSW environment.
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting CTransformers Build Process ---"

# --- Step 1: Uninstall Existing CTransformers ---
# This ensures we start with a clean slate.
echo "Uninstalling any existing ctransformers package..."
pip uninstall -y ctransformers || echo "ctransformers was not previously installed. Continuing."


# --- Step 2: Install Necessary Build Tools ---
# cmake and a C++ compiler (like gcc/g++) are required to build from source.
# We check for them first.
echo "Checking for build tools (cmake and g++)..."
if ! command -v cmake &> /dev/null || ! command -v g++ &> /dev/null; then
    echo "Build tools not found. Attempting to install them (may require sudo)..."
    # This command might vary depending on the OS (yum for CentOS, apt-get for Debian/Ubuntu)
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y cmake build-essential
    elif command -v yum &> /dev/null; then
        sudo yum install -y cmake gcc-c++
    else
        echo "ERROR: Could not find apt-get or yum. Please install 'cmake' and 'g++' manually."
        exit 1
    fi
fi
echo "Build tools are available."


# --- Step 3: Set Environment Variables to Force Build ---
# This is the most critical step. We tell pip to build the library
# from source instead of downloading a pre-compiled binary (wheel).
echo "Setting environment variables to force compilation..."
export CMAKE_ARGS="-DGGML_BUILD_TESTS=OFF"
# The --no-binary flag tells pip not to use pre-compiled wheels for ctransformers.
PIP_BUILD_FLAGS="--no-binary :all:"

echo "Environment variables set."
echo "CMAKE_ARGS=${CMAKE_ARGS}"
echo "PIP_BUILD_FLAGS=${PIP_BUILD_FLAGS}"


# --- Step 4: Install CTransformers from Source ---
# We use the version specified in your requirements file.
# The --verbose flag is added to show the compilation process.
CT_VERSION="ctransformers==0.2.24"
echo "Installing ${CT_VERSION} from source. This may take several minutes..."

pip install ${PIP_BUILD_FLAGS} --verbose "${CT_VERSION}"


# --- Step 5: Verification ---
echo "--- Verification Step ---"
echo "Verifying the new installation..."

# This command will check if the library can be imported and if it's linked correctly.
python -c "from ctransformers import AutoModelForCausalLM; print('✅ SUCCESS: ctransformers library imported successfully.')"

echo "------------------------------------------------"
echo "✅ Build and installation complete."
echo "The ctransformers library is now compiled for your specific environment."
echo "You can now run your main application script:"
echo "python app_py36_compatible.py"
echo "------------------------------------------------"
