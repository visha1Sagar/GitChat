# DataIngestion/issue_tracker_api.py
from github import Github
from typing import List, Dict, Optional
from datetime import datetime
from DataIngestion.code_message_vectorizer import CodeMessageVectorizer # Import Vectorizer


class IssueTrackerAPI:
    def __init__(self, github_token: Optional[str] = None, repo_name: str="visha1Sagar/GitChat"):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
        self.vectorizer = CodeMessageVectorizer() # Initialize vectorizer here

    def fetch_repo_issues(self, repo_name: str) -> List[Dict]:
        """Fetch issues and discussions from a GitHub repository and vectorize them."""
        issues = []
        issue_vectors = [] # To store vectors for issues.

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


        issue_vectors_list = self.vectorizer.vectorize_issues(issues) # Vectorize all issues after fetching
        for i, issue in enumerate(issues): # Add vectors back to issue data
            issue['vector'] = issue_vectors_list[i] # Store vector in each issue dict.

        return issues # Return issues with vectors


    def search_issue_discussions(self, repo_name: str, keywords: List[str]) -> List[Dict]:
        """Search issues containing keywords (remains as is, keyword search)."""
        repo = self.github.get_repo(repo_name)
        query = "+".join(keywords) + "+repo:" + repo_name
        results = self.github.search_issues(query)

        return [{
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "url": issue.html_url
        } for issue in results]