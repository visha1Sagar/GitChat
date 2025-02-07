import pandas as pd

from Memory.conversation_history import ConversationHistory
from Memory.temporal_linker import TemporalLinker


class MemoryModule:
    def __init__(self, commit_df: pd.DataFrame, storage_path: str = "sessions"):
        self.history = ConversationHistory(storage_path)
        self.linker = TemporalLinker(commit_df)

    def add_conversation(self, query: str, answer: str) -> None:
        self.history.add_entry(query, answer)

    def get_context(self, lookback_days: int = 7) -> str:
        recent = self.history.get_recent_history(lookback_days)
        return self.linker.generate_temporal_context(recent)