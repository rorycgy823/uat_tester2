#!/bin/bash

# =================================================================
# Robust Server Launcher for CDSW
# =================================================================
# This script solves the "Address already in use" (OSError 98) by
# ensuring any old process using the application port is terminated
# before launching the new application.
# =================================================================

set -e

# Get the port assigned by CDSW, defaulting to 8080 if not set.
# CDSW Applications typically use 8080 or 8100.
PORT=${CDSW_APP_PORT:-8080}

echo "--- Preparing to launch application on port ${PORT} ---"

# Find the Process ID (PID) of any process currently using the port.
# The `lsof` command lists open files and network connections.
PID=$(lsof -t -i:${PORT} || echo "")

if [ -n "$PID" ]; then
    echo "Found old process with PID ${PID} using port ${PORT}."
    echo "Terminating the old process..."
    # Use kill -9 to forcefully terminate the stuck process.
    kill -9 ${PID}
    # Wait a moment for the OS to release the port.
    sleep 2
    echo "Old process terminated."
else
    echo "Port ${PORT} is free. No old process found."
fi

echo "--- Launching the Python application ---"
# Execute the main Python application script.
python3.10 app_llama.py
