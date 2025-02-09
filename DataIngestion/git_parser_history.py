# git_history_parser.py
import git
import github
import pandas as pd
from datetime import datetime
from typing import List, Dict


class GitHistoryParser:
    def __init__(self, **kwargs):  # Use kwargs consistently
        if not kwargs:  # Check if kwargs is empty
            raise ValueError("At least one argument is required (e.g., repo_url)")

        if "repo_url" in kwargs:
            self.repo = git.Repo.clone_from(kwargs["repo_url"], "repo_directory")
        elif "repo" in kwargs and isinstance(kwargs["repo"], git.Repo):
             self.repo = kwargs["repo"]
        else:
            raise ValueError("Either 'repo_url' or a git.Repo object must be provided.")



    def parse_commit_history(self) -> pd.DataFrame:
        """Parse git commit history into structured DataFrame"""
        commits_data = []

        for commit in self.repo.iter_commits():
            commit_data = {
                "hash": commit.hexsha,
                "author": commit.author.name,
                "email": commit.author.email,
                "date": datetime.fromtimestamp(commit.authored_date),
                "message": commit.message.strip(),
                "files_changed": [item for item in commit.stats.files.keys()]
            }
            commits_data.append(commit_data)

        return pd.DataFrame(commits_data)