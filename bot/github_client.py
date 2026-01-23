import os
from github import Github

g = Github(os.getenv("GITHUB_TOKEN"))

def comment_on_pr(repo_name, pr_number, message):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)