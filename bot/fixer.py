import subprocess
from llm_engine import ask_llm

def generate_fix(logs: str):
    prompt = f"""
You are fixing a GitHub Actions CI failure.
Generate a git diff patch to fix the issue.

Only output valid git diff.

LOGS:
{logs}
"""
    return ask_llm(prompt)


def apply_patch(patch: str):
    try:
        process = subprocess.Popen(
            ["git", "apply"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.communicate(patch.encode())
        return True
    except Exception:
        rollback()
        return False


def rollback():
    subprocess.run(["git", "reset", "--hard", "HEAD~1"])