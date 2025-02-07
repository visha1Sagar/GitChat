# conversation_history.py
from datetime import datetime
import re
from typing import List, Dict, Optional
import json
from pathlib import Path

class ConversationHistory:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self.history: List[Dict] = []
        self._load_history()

    def _load_history(self):
        if self.storage_path and self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                self.history = json.load(f)

    def _save_history(self):
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.history, f, default=str)

    def _extract_entities(self, text: str) -> Dict:
        """Extract code-related entities from text"""
        return {
            'files': list(set(re.findall(r"\b[\w/-]+\.\w{2,5}\b", text))),
            'commits': re.findall(r"\b[a-f0-9]{7,}\b", text.lower()),
            'issues': list(set(re.findall(r"#(\d+)", text)))
        }

    def add_entry(self, query: str, answer: str) -> None:
        """Store conversation context with extracted entities"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'answer': answer,
            'entities': {
                **self._extract_entities(query),
                **self._extract_entities(answer)
            }
        }
        self.history.append(entry)
        self._save_history()

    def get_recent_history(self, lookback_days: int = 7) -> List[Dict]:
        """Get recent conversations within time window"""
        cutoff = datetime.now().timestamp() - (lookback_days * 86400)
        return [
            entry for entry in self.history
            if datetime.fromisoformat(entry['timestamp']).timestamp() > cutoff
        ]