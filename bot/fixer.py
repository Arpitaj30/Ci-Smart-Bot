import subprocess

def apply_patch(patch: str):
    try:
        p = subprocess.Popen(
            ["git", "apply"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        p.communicate(patch.encode())
        return True
    except Exception:
        subprocess.run(["git", "reset", "--hard"])
        return False

def commit_and_push():
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "CI Bot auto-fix"])
    subprocess.run(["git", "push"])