@echo off
REM Setup and run the CI/CD Bot on Windows

echo Setting up AI CI/CD Fix Bot...

REM Activate virtual environment if it exists
if exist "myenv\Scripts\activate.bat" (
    call myenv\Scripts\activate.bat
    echo ✓ Virtual environment activated
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo ✓ Dependencies installed

REM Check if environment file exists
if not exist ".env" (
    echo ⚠ .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please configure your .env file with GitHub App and LLM credentials
    exit /b 1
)

REM Run the application
echo.
echo Starting CI/CD Bot on http://0.0.0.0:8000
echo Health check: http://localhost:8000/health
echo Webhook endpoint: http://localhost:8000/github/webhook
echo.

uvicorn bot.app:app --host 0.0.0.0 --port 8000 --reload
