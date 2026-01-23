# from flask import Flask, request, jsonify
# from error_analyzer import analyze_error
# from fixer import generate_patch, apply_patch
# from github_client import comment_on_pr, commit_and_push
# from memory import save_patch, load_patch

# app = Flask(__name__)

# @app.route("/analyze", methods=["POST"])
# def analyze():
#     data = request.json
#     logs = data["logs"]
#     repo = data["repo"]
#     pr = int(data["pr_number"])

#     analysis, patch = analyze_error(logs)

#     save_patch(repo, pr, patch)

#     comment_on_pr(
#         repo, pr,
#         f"""
# **CI FAILED**

# ###  Root Cause
# {analysis}

# ###  Auto-Fix Ready
# Reply **`/fix`** to apply the patch automatically.
# """
#     )

#     return jsonify({"status": "analysis_posted"})

# @app.route("/apply-fix", methods=["POST"])
# def apply_fix():
#     data = request.json
#     repo = data["repo"]
#     pr = int(data["pr_number"])

#     patch = load_patch(repo, pr)
#     success = apply_patch(patch)

#     if success:
#         commit_and_push()
#         return jsonify({"status": "fix_applied"})
#     else:
#         return jsonify({"status": "fix_failed"}), 500

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)





from urllib import request
from fastapi import FastAPI
from error_analyzer import analyze_error
from fixer import generate_patch, apply_patch
from github_client import comment_on_pr, commit_and_push
from memory import save_patch, load_patch

app = FastAPI(title="AI CI Fix Bot")

@app.post("/analyze")
def analyze_ci(request: AnalyzeRequest):
    analysis = analyze_logs(request.logs)

    if not analysis["can_fix"]:
        return {
            "status": "ignored",
            "reason": analysis["reason"]
        }

    result = handle_fix(
        repo=request.repo,
        logs=request.logs,
        pr_number=request.pr_number
    )

    return {
        "status": "fix_triggered",
        "result": result
    }


@app.route("/apply-fix", methods=["POST"])
def apply_fix():
    data = request.json
    repo = data["repo"]
    pr = int(data["pr_number"])

    patch = load_patch(repo, pr)
    success = apply_patch(patch)

    if success:
        commit_and_push()
        return jsonify({"status": "fix_applied"})
    else:
        return jsonify({"status": "fix_failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
