"""
Entry point for the CI/CD Bot application.
Run with: python -m main
Or: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import os
from bot.app import app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENV", "production") == "development"
    )
