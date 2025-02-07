# git_history_parser.py
import git
import pandas as pd
from datetime import datetime
from typing import List, Dict


class GitHistoryParser:
    def __init__(self, repo_path: str = "."):
        self.repo = git.Repo(repo_path)

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
                "files_changed": [item.a_path for item in commit.stats.files]
            }
            commits_data.append(commit_data)

        return pd.DataFrame(commits_data)