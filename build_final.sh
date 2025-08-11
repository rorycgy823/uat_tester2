#!/bin/bash

# =================================================================
# FINAL Build Script for CTransformers
# =================================================================
# This script resolves all previous issues:
# 1. 'GLIBC' incompatibility by building from source.
# 2. 'Connection timed out' by using local build tools.
# 3. 'Ninja vs. Make' conflict by ensuring a modern, compatible
#    version of Ninja is installed and used correctly.
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting FINAL CTransformers Build Process ---"

# --- Step 1: Uninstall Existing CTransformers ---
echo "Uninstalling any existing ctransformers package for a clean build..."
pip uninstall -y ctransformers || echo "ctransformers was not previously installed. Continuing."


# --- Step 2: Install/Upgrade Build Dependencies ---
# We ensure modern, compatible versions of the build tools are
# installed via pip. Using --prefer-binary makes this step faster
# and more reliable if wheels are available in your Nexus.
echo "Installing/upgrading build dependencies (cmake, scikit-build, ninja)..."
pip install --upgrade --prefer-binary "cmake>=3.18" "scikit-build>=0.13" "ninja"


# --- Step 3: Set Environment Variables for Build ---
# We only need to set the essential CMAKE_ARGS. By installing ninja via pip,
# scikit-build will automatically find and use it, resolving the conflict.
echo "Setting environment variables for compilation..."
export CMAKE_ARGS="-DGGML_BUILD_TESTS=OFF"


# --- Step 4: Install CTransformers from Source ---
# The --no-binary flag is critical. It forces pip to compile the package
# instead of downloading a pre-built (and incompatible) version.
CT_VERSION="ctransformers==0.2.24"
echo "Installing ${CT_VERSION} from source. This may take several minutes..."

pip install --no-binary ctransformers --verbose "${CT_VERSION}"


# --- Step 5: Verification ---
echo "--- Verification Step ---"
echo "Verifying the new installation..."

# This command confirms the library is correctly built and installed.
python -c "from ctransformers import AutoModelForCausalLM; print('✅ SUCCESS: ctransformers library imported successfully.')"

echo "------------------------------------------------"
echo "✅ FINAL BUILD COMPLETE."
echo "All known issues should now be resolved."
echo "You can now run your main application script:"
echo "python app_py36_compatible.py"
echo "------------------------------------------------"
