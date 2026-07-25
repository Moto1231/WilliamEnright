@echo off
REM Run the AI Chat API

echo 🚀 Starting AI Chat API...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
