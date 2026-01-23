import subprocess
import logging

logger = logging.getLogger(__name__)

def apply_patch(patch: str) -> bool:
    """Apply git patch safely"""
    try:
        if not patch or len(patch.strip()) < 10:
            return False
        
        p = subprocess.Popen(
            ["git", "apply", "--check"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate(patch.encode())
        
        if p.returncode != 0:
            logger.warning(f"Patch validation failed: {stderr.decode()}")
            return False
        
        # Apply the patch
        p = subprocess.Popen(
            ["git", "apply"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        p.communicate(patch.encode())
        return p.returncode == 0
    except Exception as e:
        logger.error(f"Error applying patch: {str(e)}")
        return False

def commit_and_push(commit_msg: str = "CI Bot auto-fix") -> bool:
    """Commit and push changes"""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push"], check=True)
        return True
    except Exception as e:
        logger.error(f"Error committing: {str(e)}")
        return False