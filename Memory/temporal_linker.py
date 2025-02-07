# temporal_linker.py
from datetime import datetime
from typing import List, Dict
import pandas as pd


class TemporalLinker:
    def __init__(self, commit_df: pd.DataFrame):
        self.commit_df = commit_df
        self.commit_df['date'] = pd.to_datetime(self.commit_df['date'])

    def _find_code_changes(self, file_paths: List[str], after_date: datetime) -> pd.DataFrame:
        """Find commits affecting mentioned files after a given date"""
        if not file_paths:
            return pd.DataFrame()

        return self.commit_df[
            (self.commit_df['date'] > after_date) &
            (self.commit_df['files_changed'].apply(
                lambda files: any(f in file_paths for f in files)
            ))
            ]

    def _find_related_commits(self, commit_hashes: List[str]) -> pd.DataFrame:
        """Find subsequent commits to the same files"""
        if not commit_hashes:
            return pd.DataFrame()

        # Get files from original commits
        original_files = set()
        for commit_hash in commit_hashes:
            files = self.commit_df[self.commit_df['hash'] == commit_hash]['files_changed']
            if not files.empty:
                original_files.update(files.iloc[0])

        # Find later commits touching these files
        latest_commit_date = self.commit_df[self.commit_df['hash'].isin(commit_hashes)]['date'].max()
        return self.commit_df[
            (self.commit_df['date'] > latest_commit_date) &
            (self.commit_df['files_changed'].apply(
                lambda files: any(f in original_files for f in files)
            ))
            ]

    def find_temporal_links(self, conversation_entry: Dict) -> Dict:
        """Identify relevant code changes since a conversation"""
        entry_date = datetime.fromisoformat(conversation_entry['timestamp'])
        entities = conversation_entry['entities']

        return {
            'file_changes': self._find_code_changes(
                entities['files'], entry_date
            ).to_dict('records'),
            'commit_followups': self._find_related_commits(
                entities['commits']
            ).to_dict('records'),
            'issue_updates': [],  # Could integrate issue tracker here
            'entry_date': entry_date.isoformat(),
            'current_date': datetime.now().isoformat()
        }

    def generate_temporal_context(self, history: List[Dict]) -> str:
        """Create natural language summary of relevant changes"""
        context = []

        for entry in history[-3:]:  # Last 3 conversations
            links = self.find_temporal_links(entry)

            if links['file_changes']:
                files = {f for c in links['file_changes'] for f in c['files_changed']}
                context.append(
                    f"Since your question on {entry['timestamp'][:10]} about {', '.join(files)}: "
                    f"{len(links['file_changes'])} subsequent commits were made"
                )

            if links['commit_followups']:
                original_commits = entry['entities']['commits'][:2]
                context.append(
                    f"After your discussion of commits {', '.join(original_commits)}: "
                    f"{len(links['commit_followups'])} follow-up commits were added"
                )

        return "\n".join(context) if context else "No recent changes to discussed items"