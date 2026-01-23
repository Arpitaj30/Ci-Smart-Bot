from llm_engine import ask_llm

def analyze_error(logs: str):
    
    analysis_prompt = f"""
You are a senior DevOps engineer.
Analyze these GitHub Actions logs and explain the root cause briefly.

LOGS:
{logs}
"""
    fix_prompt = f"""
Generate a valid git diff patch to fix the CI failure.
Only output the diff.

LOGS:
{logs}
"""

    analysis = ask_llm(analysis_prompt)
    patch = ask_llm(fix_prompt)

    return analysis, patch