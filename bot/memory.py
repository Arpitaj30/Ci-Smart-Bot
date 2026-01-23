import os
import json

DB = "patch_store.json"

def save_patch(repo, pr, patch):
    data = {}
    if os.path.exists(DB):
        data = json.load(open(DB))

    data[f"{repo}#{pr}"] = patch
    json.dump(data, open(DB, "w"))

def load_patch(repo, pr):
    data = json.load(open(DB))
    return data.get(f"{repo}#{pr}")