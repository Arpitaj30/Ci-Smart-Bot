import os
from pdb import run
from github import Github, GithubIntegration
from typing import Optional

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")


class GitHubClient:
    def __init__(self, app_id: str = None, private_key: str = None, token: str = None):
        """Initialize GitHub client with App or token"""
        if app_id and private_key:
            
            self.integration = GithubIntegration(int(app_id), private_key)
            self.github = None
        else:
            self.github = Github(token or os.getenv("GITHUB_TOKEN"))
            self.integration = None
    
    def get_repo(self, repo_full_name: str, installation_id: Optional[int] = None):
        """Get repository instance"""
        if self.integration and installation_id:
            return self.integration.get_repo(repo_full_name, installation_id)
        return self.github.get_repo(repo_full_name)
    
    def get_pr_from_run(self, repo_name, run_id, installation_id):
        repo = self.get_repo(repo_name, installation_id)
        run = repo.get_workflow_run(run_id)
        prs = run.pull_requests
        return prs[0].number if prs else None

    
    def comment_on_pr(self, repo_name: str, pr_number: int, message: str, installation_id: Optional[int] = None):
        """Post comment on PR"""
        repo = self.get_repo(repo_name, installation_id)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(message)
    
    def get_workflow_logs(self, repo_name: str, run_id: int, installation_id: Optional[int] = None) -> str:
        """Get workflow run logs"""
        repo = self.get_repo(repo_name, installation_id)
        run = repo.get_workflow_run(run_id)
        return run.raw_data.get("conclusion", "unknown")
        # return run.get_logs().decode("utf-8")