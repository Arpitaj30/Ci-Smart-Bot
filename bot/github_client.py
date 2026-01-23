import os
import subprocess
from github import Github

token = os.getenv("GITHUB_TOKEN")
g = Github(token)

def comment_on_pr(repo_name, pr_number, message):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)


def commit_and_push(message="CI Bot auto-fix"):
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", message])
    subprocess.run(["git", "push"])