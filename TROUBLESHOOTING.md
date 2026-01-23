# Troubleshooting Guide

## Common Issues and Solutions

### 1. ModuleNotFoundError: No module named 'bot_runner'

**Problem**: Import errors when trying to run the application.

**Solution**:
- Make sure you're running from the project **root directory** (`BOT_AGENT_CICD/`), not from inside the `bot/` folder
- The correct command is: `uvicorn bot.app:app --host 0.0.0.0 --port 8000`
- NOT: `cd bot && uvicorn app:app ...` ❌

### 2. Import Errors

**Problem**: Various import errors between modules.

**Solution**:
All modules now use relative imports (`.module_name`). This is correct for a package structure.

### 3. ModuleNotFoundError: No module named 'github'

**Problem**: PyGithub not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

### 4. ModuleNotFoundError: No module named 'fastapi'

**Problem**: Dependencies not installed.

**Solution**:
```bash
# Make sure virtual environment is activated
myenv\Scripts\activate  # Windows
# or
source myenv/bin/activate  # Linux/Mac

# Then install
pip install -r requirements.txt
```

### 5. API Key Not Configured

**Problem**: LLM calls failing with authentication errors.

**Solution**:
Create a `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env and add your keys
```

Required variables:
- `GITHUB_APP_ID`
- `GITHUB_PRIVATE_KEY`
- `GROQ_API_KEY` (or `OPENAI_API_KEY`)

### 6. GitHub App Integration Issues

**Problem**: Webhook not receiving events.

**Check**:
1. GitHub App webhook URL is correct: `https://your-domain.com/github/webhook`
2. Webhook secret is configured (if using)
3. App has correct permissions (pull_requests, contents, workflows)
4. App is installed on the repository

### 7. Server Won't Start

**Problem**: Uvicorn fails to start.

**Solution**:
```bash
# Test import first
python test_imports.py

# Check for port conflicts
# Try different port
uvicorn bot.app:app --host 0.0.0.0 --port 8080

# Check if virtual environment is activated
which python  # should show myenv path
```

### 8. Relative Import Errors

**Problem**: `ImportError: attempted relative import with no known parent package`

**Solution**:
Never run individual Python files directly:
```bash
# ❌ Don't do this
python bot/app.py

# ✓ Do this instead
uvicorn bot.app:app --host 0.0.0.0 --port 8000
```

## Verification Steps

### 1. Test Imports
```bash
python test_imports.py
```

Should output:
```
✓ bot package imported successfully
✓ bot.app imported successfully
✓ FastAPI app instance is valid
```

### 2. Check Dependencies
```bash
pip list | grep -E "fastapi|uvicorn|PyGithub|requests"
```

Should show:
- fastapi
- uvicorn
- PyGithub
- requests
- pydantic
- python-dotenv

### 3. Test Health Endpoint
```bash
# Start server in one terminal
uvicorn bot.app:app --host 0.0.0.0 --port 8000

# In another terminal
curl http://localhost:8000/health
```

Should return:
```json
{"status":"running"}
```

## Debug Mode

Run with verbose logging:
```bash
LOG_LEVEL=DEBUG uvicorn bot.app:app --host 0.0.0.0 --port 8000 --log-level debug
```

## Need Help?

1. Check you're in the right directory: `pwd` should end with `BOT_AGENT_CICD`
2. Check virtual environment: `which python` should show `myenv`
3. Verify file structure:
   ```
   BOT_AGENT_CICD/
   ├── bot/
   │   ├── __init__.py  ← Must exist
   │   ├── app.py
   │   └── ...
   ├── main.py
   ├── requirements.txt
   └── .env
   ```
