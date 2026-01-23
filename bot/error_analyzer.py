from llm_engine import ask_llm

def analyze_error(logs: str):
    prompt = f"""
You are a DevOps CI/CD expert.
Analyze the following GitHub Actions error logs.
Explain the root cause briefly and suggest a fix.

LOGS:
{logs}
"""

    response = ask_llm(prompt)

    return {
        "analysis": response
    }