# Quick Start Guide

Get your AI CI/CD Fix Bot running in 5 minutes! 🚀

## Prerequisites

- Python 3.8+
- Git
- GitHub App credentials (App ID + Private Key)
- LLM API key (Groq or OpenAI)

## Step 1: Setup Environment

```bash
# Navigate to project directory
cd BOT_AGENT_CICD

# Activate virtual environment (if exists)
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Credentials

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Windows:
notepad .env
# Linux/Mac:
nano .env
```

Required credentials in `.env`:
```bash
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
```

## Step 3: Run the Bot

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
bash run.sh
```

### Manual Start
```bash
uvicorn bot.app:app --host 0.0.0.0 --port 8000 --reload
```

## Step 4: Verify It's Running

Open your browser or use curl:
```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"running"}
```

## Step 5: Configure GitHub App Webhook

1. Go to your GitHub App settings
2. Set Webhook URL: `https://your-domain.com/github/webhook`
3. Subscribe to events:
   - ✅ workflow_run
   - ✅ pull_request
4. Save changes

## Step 6: Install App on Repository

1. Install the GitHub App on your target repository
2. Grant required permissions:
   - Pull requests: Read & Write
   - Contents: Read & Write
   - Workflows: Read

## Step 7: Test It!

1. Create a PR that breaks CI/CD
2. Wait for workflow to fail
3. Bot will:
   - Analyze the error
   - Generate a patch
   - Comment on the PR with analysis and fix

## Troubleshooting

If something doesn't work:
1. Check `TROUBLESHOOTING.md`
2. Run `python test_imports.py` to verify setup
3. Check logs in terminal where bot is running

## Next Steps

- Review [README.md](README.md) for detailed documentation
- Check [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) for architecture details
- Configure LLM model and parameters in `.env`

## Production Deployment

For production, consider:
- Using a proper web server (Nginx + Gunicorn)
- SSL/TLS for webhook endpoint
- Environment variable management (Docker secrets, AWS Secrets Manager)
- Logging to external service (CloudWatch, Datadog)
- Health monitoring and alerts

## Support

Need help? Check:
- `TROUBLESHOOTING.md` - Common issues
- `README.md` - Full documentation  
- GitHub App documentation - https://docs.github.com/en/apps

Enjoy your automated CI/CD fixer! 🎉
