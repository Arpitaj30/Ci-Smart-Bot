@REM @echo off
@REM REM Setup and run the CI/CD Bot on Windows

@REM echo Setting up AI CI/CD Fix Bot...

@REM REM Activate virtual environment if it exists
@REM if exist "myenv\Scripts\activate.bat" (
@REM     call myenv\Scripts\activate.bat
@REM     echo ✓ Virtual environment activated
@REM )

@REM REM Install dependencies
@REM echo Installing dependencies...
@REM pip install -q -r requirements.txt
@REM echo ✓ Dependencies installed

@REM REM Check if environment file exists
@REM if not exist ".env" (
@REM     echo ⚠ .env file not found. Creating from .env.example...
@REM     copy .env.example .env
@REM     echo Please configure your .env file with GitHub App and LLM credentials
@REM     exit /b 1
@REM )

@REM REM Run the application
@REM echo.
@REM echo Starting CI/CD Bot on http://0.0.0.0:8000
@REM echo Health check: http://localhost:8000/health
@REM echo Webhook endpoint: http://localhost:8000/github/webhook
@REM echo.

@REM uvicorn bot.app:app --host 0.0.0.0 --port 8000 --reload
