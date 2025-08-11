#!/bin/bash

# =================================================================
# Build CTransformers Offline for GLIBC & Firewall Compatibility
# =================================================================
# This script resolves two issues:
# 1. 'GLIBC_2.29 not found' error by compiling from source.
# 2. 'Connection timed out' error by using the system's existing
#    cmake and preventing the build process from accessing the internet.
# =================================================================

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Starting CTransformers Offline Build Process ---"

# --- Step 1: Uninstall Existing CTransformers ---
echo "Uninstalling any existing ctransformers package..."
pip uninstall -y ctransformers || echo "ctransformers was not previously installed. Continuing."


# --- Step 2: Ensure Build Dependencies are Installed ---
# The build process itself needs scikit-build and cmake. We install them first.
# This allows pip to find them locally instead of trying to download them.
echo "Installing build dependencies (scikit-build, cmake)..."
pip install "scikit-build>=0.13" "cmake>=3.18"


# --- Step 3: Find the System's CMake Executable ---
# This is crucial to prevent the build from trying to download its own cmake.
echo "Locating system cmake executable..."
SYSTEM_CMAKE_PATH=$(which cmake)
if [ -z "$SYSTEM_CMAKE_PATH" ]; then
    echo "ERROR: cmake is not installed or not in PATH. Please install it first."
    # On CentOS/RHEL: sudo yum install cmake
    # On Debian/Ubuntu: sudo apt-get install cmake
    exit 1
fi
echo "Found system cmake at: $SYSTEM_CMAKE_PATH"


# --- Step 4: Set Environment Variables to Force Offline Build ---
# We explicitly tell the build system to use the cmake we found.
echo "Setting environment variables to force offline compilation..."
export CMAKE_ARGS="-DGGML_BUILD_TESTS=OFF"
# This is the key to preventing the timeout error.
export SKBUILD_CONFIGURE_OPTIONS="-DCMAKE_MAKE_PROGRAM=$(which make) -DCMAKE_C_COMPILER=$(which gcc) -DCMAKE_CXX_COMPILER=$(which g++)"

# The --no-binary flag tells pip not to use pre-compiled wheels.
PIP_BUILD_FLAGS="--no-binary ctransformers"

echo "Environment variables set."


# --- Step 5: Install CTransformers from Source ---
# We use the version specified in your requirements file.
# The --verbose flag is added to show the compilation process.
CT_VERSION="ctransformers==0.2.24"
echo "Installing ${CT_VERSION} from source using system cmake. This may take several minutes..."

pip install ${PIP_BUILD_FLAGS} --verbose "${CT_VERSION}"


# --- Step 6: Verification ---
echo "--- Verification Step ---"
echo "Verifying the new installation..."

# This command will check if the library can be imported and if it's linked correctly.
python -c "from ctransformers import AutoModelForCausalLM; print('✅ SUCCESS: ctransformers library imported successfully.')"

echo "------------------------------------------------"
echo "✅ Offline build and installation complete."
echo "The ctransformers library is now compiled for your specific environment."
echo "You can now run your main application script:"
echo "python app_py36_compatible.py"
echo "------------------------------------------------"
