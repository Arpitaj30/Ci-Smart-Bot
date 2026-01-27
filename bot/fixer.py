import subprocess
import logging

logger = logging.getLogger(__name__)


def apply_patch(patch: str) -> bool:
    try:
        p = subprocess.Popen(
            ["git", "apply", "--check"],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, err = p.communicate(patch.encode())

        if p.returncode != 0:
            logger.error("Patch validation failed:\n" + err.decode())
            return False

        subprocess.run(["git", "apply"], input=patch.encode(), check=True)
        logger.info("Patch applied successfully")
        return True

    except Exception:
        logger.error("Patch apply failed", exc_info=True)
        return False


def commit_and_push(msg: str = "CI Bot auto-fix") -> bool:
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"]).decode()
        if not status.strip():
            logger.warning("No changes to commit")
            return False

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)

        logger.info("Changes pushed successfully")
        return True

    except Exception:
        logger.error("Commit/push failed", exc_info=True)
        return False