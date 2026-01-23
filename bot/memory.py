import os
import json
import logging

logger = logging.getLogger(__name__)

DB_FILE = os.getenv("PATCH_DB", "patch_store.json")

def save_patch(repo: str, pr: int, patch: str) -> bool:
    """Save patch to store"""
    try:
        data = {}
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                data = json.load(f)
        
        data[f"{repo}#{pr}"] = patch
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        logger.error(f"Error saving patch: {str(e)}")
        return False

def load_patch(repo: str, pr: int) -> str:
    """Load patch from store"""
    try:
        if not os.path.exists(DB_FILE):
            return ""
        with open(DB_FILE, "r") as f:
            data = json.load(f)
        return data.get(f"{repo}#{pr}", "")
    except Exception as e:
        logger.error(f"Error loading patch: {str(e)}")
        return ""