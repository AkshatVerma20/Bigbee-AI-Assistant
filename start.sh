#!/bin/bash
# Quick-start script — runs backend and frontend in separate terminals
set -e

# Check .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Run: cp .env.example .env"
    echo "   Then add your OPENAI_API_KEY to .env"
    exit 1
fi

# Check OPENAI_API_KEY is set
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-key-here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env"
    exit 1
fi

echo "✅ .env looks good"
echo ""
echo "Starting backend on http://localhost:8000 ..."
echo "Starting frontend on http://localhost:8501 ..."
echo ""
echo "Press Ctrl+C to stop."
echo ""

# Start backend in background
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend
sleep 3

# Start frontend
streamlit run frontend/app.py --server.port 8501

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null
