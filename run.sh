#!/bin/bash
# Setup and run the CI/CD Bot

echo "Setting up AI CI/CD Fix Bot..."

# Activate virtual environment if it exists
if [ -f "myenv/Scripts/activate" ]; then
    source myenv/Scripts/activate
    echo "✓ Virtual environment activated"
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check if environment file exists
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please configure your .env file with GitHub App and LLM credentials"
    exit 1
fi

# Run the application
echo "Starting CI/CD Bot on http://0.0.0.0:8000"
echo "Health check: http://localhost:8000/health"
echo "Webhook endpoint: http://localhost:8000/github/webhook"
echo ""

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
