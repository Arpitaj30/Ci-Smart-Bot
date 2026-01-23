import os
import requests
import logging

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "groq")  # groq, openai, local
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY")
        self.model = os.getenv("LLM_MODEL", "llama3-70b-8192" if self.provider == "groq" else "gpt-4")
    
    def ask(self, prompt: str) -> str:
        """Get LLM response"""
        try:
            if self.provider == "groq":
                return self._ask_groq(prompt)
            elif self.provider == "openai":
                return self._ask_openai(prompt)
            else:
                return f"Provider {self.provider} not configured"
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return ""
    
    def _ask_groq(self, prompt: str) -> str:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 500
            },
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    
    def _ask_openai(self, prompt: str) -> str:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 500
            },
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

_engine = LLMEngine()

def ask_llm(prompt: str) -> str:
    """Ask LLM a question"""
    return _engine.ask(prompt)