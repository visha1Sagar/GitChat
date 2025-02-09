# issue_tracker_api.py
from github import Github
from typing import List, Dict, Optional
from datetime import datetime


class IssueTrackerAPI:
    def __init__(self, github_token: Optional[str] = None, repo_name: str="visha1Sagar/GitChat"):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)

    def fetch_repo_issues(self, repo_name: str) -> List[Dict]:
        """Fetch issues and discussions from a GitHub repository"""

        issues = []

        for issue in self.repo.get_issues(state="all"):
            issue_data = {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "created_at": issue.created_at,
                "closed_at": issue.closed_at,
                "body": issue.body,
                "comments": [
                    {
                        "author": comment.user.login,
                        "body": comment.body,
                        "created_at": comment.created_at
                    } for comment in issue.get_comments()
                ]
            }
            issues.append(issue_data)

        return issues

    def search_issue_discussions(self, repo_name: str, keywords: List[str]) -> List[Dict]:
        """Search issues containing keywords"""
        repo = self.github.get_repo(repo_name)
        query = "+".join(keywords) + "+repo:" + repo_name
        results = self.github.search_issues(query)

        return [{
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "url": issue.html_url
        } for issue in results]