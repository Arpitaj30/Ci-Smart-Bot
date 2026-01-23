# AI CI/CD Fix Bot

An intelligent bot that automatically analyzes and fixes CI/CD pipeline failures across multiple GitHub repositories using GitHub App integration.

## Features

- 🤖 **Multi-Repo Support**: Works seamlessly across multiple repositories
- 🔧 **Automatic Fix Generation**: Uses LLM (Groq/OpenAI) to analyze errors and generate patches
- 📝 **GitHub App Integration**: Secure webhook-based authentication
- 🚀 **FastAPI Server**: Async webhook handling
- 💾 **Patch Storage**: Stores patches for review before applying

## Architecture

```
bot/
├── app.py              # FastAPI webhook server
├── bot_runner.py       # Main bot logic and GitHub event handler
├── github_client.py    # GitHub App client (multi-repo support)
├── error_analyzer.py   # Error analysis using LLM
├── fixer.py           # Patch application and git operations
├── llm_engine.py      # LLM provider abstraction (Groq/OpenAI)
├── memory.py          # Patch storage and retrieval
└── server.py          # Legacy file (use app.py instead)
```

## Setup

### 1. GitHub App Configuration

Create a GitHub App with the following permissions:

**Repository Permissions:**
- `pull_requests`: Read & Write
- `checks`: Read
- `contents`: Read & Write
- `workflows`: Read

**Subscribe to Events:**
- `workflow_run`
- `pull_request`

### 2. Environment Variables

```bash
# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY=your_private_key_content

# LLM Provider (groq or openai)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
# OR
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key

# Optional
LLM_MODEL=llama3-70b-8192        # Groq default
PATCH_DB=patch_store.json        # Default: patch_store.json
```

### 3. Installation

```bash
# Create and activate virtual environment (if not already done)
python -m venv myenv

# Windows
myenv\Scripts\activate

# Linux/Mac
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Running the Bot

```bash
# Option 1: Quick start script
# Windows
run.bat

# Linux/Mac
bash run.sh

# Option 2: Using Python entry point
python main.py

# Option 3: Using uvicorn directly (from project root)
uvicorn bot.app:app --host 0.0.0.0 --port 8000

# Option 4: With auto-reload for development
uvicorn bot.app:app --host 0.0.0.0 --port 8000 --reload
```

**Important**: Always run from the project root directory (`BOT_AGENT_CICD/`), not from inside the `bot/` folder.

### 5. Webhook Configuration

In GitHub App settings, set the Webhook URL to:
```
https://your-domain.com/github/webhook
```

## API Endpoints

### Health Check
```
GET /health
```
Returns: `{"status": "running"}`

### GitHub Webhook
```
POST /github/webhook
```
Accepts GitHub webhook events for:
- `workflow_run` - CI workflow completion
- `pull_request` - PR opened/updated

## How It Works

1. **GitHub Event Trigger**: Workflow fails → GitHub sends webhook event
2. **Event Analysis**: Bot receives event and extracts repository/run info
3. **Error Analysis**: LLM analyzes the failure context
4. **Patch Generation**: LLM generates a git diff patch
5. **Storage**: Patch is stored in `patch_store.json`
6. **PR Comment**: Bot posts analysis and fix suggestion as PR comment
7. **Approval**: User reviews and approves the fix
8. **Application**: Patch is applied, committed, and pushed

## Code Changes

### Cleaned Up:
- ✅ Removed unused Flask/Django code
- ✅ Removed commented-out legacy endpoints
- ✅ Removed local LLM model loading (heavy dependencies)
- ✅ Removed unnecessary print statements
- ✅ Removed torch/transformers dependencies
- ✅ Fixed syntax errors in fixer.py

### Improved:
- ✅ GitHub App class for multi-repo support
- ✅ Async event handling
- ✅ Error logging with proper handlers
- ✅ Type hints for better IDE support
- ✅ Configurable LLM providers
- ✅ Patch validation before application
- ✅ Better exception handling

## Dependencies

```
fastapi          # Web framework
uvicorn          # ASGI server
requests         # HTTP requests
PyGithub         # GitHub API
python-dotenv    # Environment variables
pydantic         # Data validation
```

## Usage Example

1. Push code that breaks CI
2. GitHub workflow fails
3. Bot analyzes error via LLM
4. Bot comments on associated PR with:
   - Root cause analysis
   - Proposed fix
5. User reviews and reacts with ✅
6. Bot applies patch automatically

## Security Notes

- Private key stored as environment variable
- No hardcoded credentials
- Webhook validation via GitHub headers
- Sandbox patch application with `--check` flag

## Future Enhancements

- [ ] Reaction-based approval system
- [ ] Multiple patch strategy options
- [ ] Performance metrics tracking
- [ ] Integration tests
- [ ] Deployment documentation
