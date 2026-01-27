import os
from github import Github, GithubIntegration
from typing import Optional


class GitHubClient:
    def __init__(self, app_id: str = None, private_key: str = None, token: str = None):
        self.app_id = app_id
        self.private_key = private_key
        self.token = token or os.getenv("GITHUB_TOKEN")

        if self.app_id and self.private_key:
            self.integration = GithubIntegration(int(self.app_id), self.private_key)
            self.github = None
        else:
            self.integration = None
            self.github = Github(self.token)

    # 🔐 App → installation token
    def _get_github_for_installation(self, installation_id: int) -> Github:
        token = self.integration.get_access_token(installation_id).token
        return Github(token)

    def get_repo(self, repo_full_name: str, installation_id: Optional[int] = None):
        if installation_id:
            gh = self._get_github_for_installation(installation_id)
            return gh.get_repo(repo_full_name)
        return self.github.get_repo(repo_full_name)

    # 📜 Logs
    def get_workflow_logs(self, repo_name: str, run_id: int, installation_id: int) -> str:
        repo = self.get_repo(repo_name, installation_id)
        run = repo.get_workflow_run(run_id)
        return run.get_logs().decode("utf-8", errors="ignore")

    # 🔁 PR mapping
    def get_pr_from_run(self, repo_name: str, run_id: int, installation_id: int):
        repo = self.get_repo(repo_name, installation_id)
        run = repo.get_workflow_run(run_id)
        return run.pull_requests[0].number if run.pull_requests else None

    # 💬 Comment
    def comment_on_pr(self, repo, pr_number, message, installation_id):
        pr = self.get_repo(repo, installation_id).get_pull(pr_number)
        pr.create_issue_comment(message)

    # 🧵 Create PR
    def create_pull_request(
        self, repo, head, base, title, body, installation_id
    ):
        repo_obj = self.get_repo(repo, installation_id)
        return repo_obj.create_pull(
            title=title,
            body=body,
            head=head,
            base=base
        )

    # 🔀 Merge PR
    def merge_pr(self, repo, pr_number, installation_id):
        pr = self.get_repo(repo, installation_id).get_pull(pr_number)
        pr.merge(merge_method="squash")

    def get_installation_token(self, installation_id: int) -> str:
        token = self.integration.get_access_token(installation_id)
        return token.token