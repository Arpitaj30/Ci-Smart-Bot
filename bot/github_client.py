import os
from github import Github, GithubIntegration
from typing import Optional


class GitHubClient:
    def __init__(self, app_id: str = None, private_key: str = None, token: str = None):
        self.app_id = app_id
        self.private_key = private_key
        self.token = token or os.getenv("GITHUB_TOKEN")

        if self.app_id and self.private_key:
            self.integration = GithubIntegration(
                int(self.app_id),
                self.private_key
            )
            self.github = None
        else:
            self.integration = None
            self.github = Github(self.token)

    # 🔐 INSTALLATION TOKEN
    def get_installation_token(self, installation_id: int) -> str:
        if not self.integration:
            raise RuntimeError("GitHub App not configured")
        return self.integration.get_access_token(installation_id).token

    # 📦 REPO ACCESS
    def get_repo(self, repo_full_name: str, installation_id: Optional[int] = None):
        if installation_id:
            gh = Github(self.get_installation_token(installation_id))
            return gh.get_repo(repo_full_name)

        if self.github:
            return self.github.get_repo(repo_full_name)

        raise RuntimeError("No GitHub authentication available")

    # 🔁 WORKFLOW → PR
    def get_pr_from_run(self, repo_name: str, run_id: int, installation_id: int):
        repo = self.get_repo(repo_name, installation_id)
        run = repo.get_workflow_run(run_id)
        prs = run.pull_requests
        return prs[0].number if prs else None

    # 💬 COMMENT ON PR
    def comment_on_pr(self, repo_name: str, pr_number: int, message: str, installation_id: int):
        repo = self.get_repo(repo_name, installation_id)
        pr = repo.get_pull(pr_number)
        pr.create_issue_comment(message)

    # 📜 GET REAL WORKFLOW LOGS
    def get_workflow_logs(self, repo_name: str, run_id: int, installation_id: int) -> str:
        repo = self.get_repo(repo_name, installation_id)
        run = repo.get_workflow_run(run_id)
        return run.get_logs().decode("utf-8", errors="ignore")

    # 🔥 CREATE PULL REQUEST
    def create_pull_request(
        self,
        repo_name: str,
        branch: str,
        installation_id: int,
        title: str,
        body: str
    ):
        repo = self.get_repo(repo_name, installation_id)
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base="main"
        )
        return pr.html_url












# # import os
# # from pdb import run
# # from github import Github, GithubIntegration
# # from typing import Optional

# # GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
# # GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")
# # GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# # class GitHubClient:
# #     def __init__(self, app_id: str = None, private_key: str = None, token: str = None):
# #         """Initialize GitHub client with App or token"""
# #         if app_id and private_key:
            
# #             self.integration = GithubIntegration(int(app_id), private_key)
# #             self.github = None
# #         else:
# #             self.github = Github(token or os.getenv("GITHUB_TOKEN"))
# #             self.integration = None
    
# #     def get_repo(self, repo_full_name: str, installation_id: Optional[int] = None):
# #         """Get repository instance"""
# #         if self.integration and installation_id:
# #             return self.integration.get_repo(repo_full_name, installation_id)
# #         return self.github.get_repo(repo_full_name)
    
# #     def get_pr_from_run(self, repo_name, run_id, installation_id):
# #         repo = self.get_repo(repo_name, installation_id)
# #         run = repo.get_workflow_run(run_id)
# #         prs = run.pull_requests
# #         return prs[0].number if prs else None

    
# #     def comment_on_pr(self, repo_name: str, pr_number: int, message: str, installation_id: Optional[int] = None):
# #         """Post comment on PR"""
# #         repo = self.get_repo(repo_name, installation_id)
# #         pr = repo.get_pull(pr_number)
# #         pr.create_issue_comment(message)
    
# #     def get_workflow_logs(self, repo_name: str, run_id: int, installation_id: Optional[int] = None) -> str:
# #         """Get workflow run logs"""
# #         repo = self.get_repo(repo_name, installation_id)
# #         run = repo.get_workflow_run(run_id)
# #         return run.raw_data.get("conclusion", "unknown")
# #         # return run.get_logs().decode("utf-8")







# import os
# from github import Github, GithubIntegration
# from typing import Optional


# class GitHubClient:
#     def __init__(self, app_id: str = None, private_key: str = None, token: str = None):
#         """
#         Initialize GitHub client.
#         Prefer GitHub App auth. Token is fallback (dev only).
#         """
#         self.app_id = app_id
#         self.private_key = private_key
#         self.token = token or os.getenv("GITHUB_TOKEN")

#         if self.app_id and self.private_key:
#             self.integration = GithubIntegration(
#                 int(self.app_id),
#                 self.private_key
#             )
#             self.github = None
#         else:
#             self.integration = None
#             self.github = Github(self.token)

#     # -------------------------
#     # 🔐 Internal helper
#     # -------------------------
#     def _get_github_for_installation(self, installation_id: int) -> Github:
#         """
#         Create GitHub client using installation access token
#         """
#         if not self.integration:
#             raise RuntimeError("GitHub App integration not configured")

#         access_token = self.integration.get_access_token(installation_id).token
#         return Github(access_token)

#     # -------------------------
#     # 📦 Repo access
#     # -------------------------
#     def get_repo(self, repo_full_name: str, installation_id: Optional[int] = None):
#         if installation_id:
#             gh = self._get_github_for_installation(installation_id)
#             return gh.get_repo(repo_full_name)

#         if self.github:
#             return self.github.get_repo(repo_full_name)

#         raise RuntimeError("No GitHub authentication available")

#     # -------------------------
#     # 🔁 Workflow → PR mapping
#     # -------------------------
#     def get_pr_from_run(self, repo_name: str, run_id: int, installation_id: int):
#         repo = self.get_repo(repo_name, installation_id)
#         run = repo.get_workflow_run(run_id)

#         prs = run.pull_requests
#         return prs[0].number if prs else None

#     # -------------------------
#     # 💬 PR comments
#     # -------------------------
#     def comment_on_pr(
#         self,
#         repo_name: str,
#         pr_number: int,
#         message: str,
#         installation_id: int
#     ):
#         repo = self.get_repo(repo_name, installation_id)
#         pr = repo.get_pull(pr_number)
#         pr.create_issue_comment(message)

#     # -------------------------
#     # 📜 REAL workflow logs
#     # -------------------------
#     def get_workflow_logs(
#         self,
#         repo_name: str,
#         run_id: int,
#         installation_id: int
#     ) -> str:
#         repo = self.get_repo(repo_name, installation_id)
#         run = repo.get_workflow_run(run_id)

#         # This returns BYTES → decode to string
#         logs = run.get_logs()
#         return logs.decode("utf-8", errors="ignore")