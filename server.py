from flask import Flask, request, jsonify
from error_analyzer import analyze_error
from fixer import generate_fix

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    logs = data["logs"]
    repo = data["repo"]
    pr_number = data.get("pr_number")

    analysis = analyze_error(logs)
    patch = generate_fix(logs)

    return jsonify({
        "repo": repo,
        "analysis": analysis,
        "patch": patch
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)