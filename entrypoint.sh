#!/bin/bash
set -e

# Default command is to run FastAPI
COMMAND=${1:-"run_fastapi"}

if [ "$COMMAND" = "prepare_db" ]; then
    echo "Preparing database..."
    python prepare_db.py
elif [ "$COMMAND" = "run_fastapi" ]; then
    echo "Starting FastAPI server..."
    python run_fastapi.py
elif [ "$COMMAND" = "both" ]; then
    echo "Preparing database and then starting FastAPI server..."
    python prepare_db.py && python run_fastapi.py
else
    echo "Unknown command: $COMMAND"
    echo "Available commands: prepare_db, run_fastapi, both"
    exit 1
fi 