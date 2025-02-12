# DataIngestion/code_message_vectorizer.py
from pathlib import Path
from typing import Dict, Union, List
import numpy as np
from sentence_transformers import SentenceTransformer


class CodeMessageVectorizer:
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        self.chunk_size = 512  # tokens

    def _chunk_text(self, text: str) -> List[str]:
        """Split large texts into manageable chunks"""
        words = text.split()
        return [' '.join(words[i:i + self.chunk_size])
                for i in range(0, len(words), self.chunk_size)]

    def vectorize_codebase(self, repo_path: str) -> Dict[str, np.ndarray]: # Return type is still Dict, but now vectors inside are chunks.
        """Convert code files to vectors, chunking large files."""
        vectors = {}
        code_files = Path(repo_path).rglob('*.*')
        for i, file_path in enumerate(code_files):
            print(f"{i} - Vectorizing file:", file_path)
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        chunks = self._chunk_text(content)
                        vectors[str(file_path)] = self.model.encode(chunks) # Now storing list of vectors per file
                except UnicodeDecodeError:
                    continue  # Skip binary files
        return vectors

    def vectorize_commit_messages(self, messages: List[str]) -> np.ndarray:
        """Convert commit messages to vectors"""
        return np.array(self.model.encode(messages)) # Directly return numpy array for messages

    def vectorize_issues(self, issues: List[Dict]) -> List[np.ndarray]: # New function to vectorize issues.
        """Vectorize issue titles and bodies."""
        issue_vectors = []
        for issue in issues:
            text_to_vectorize = f"Title: {issue['title']}\nBody: {issue['body']}" # Combine title and body
            issue_vector = self.model.encode(text_to_vectorize)
            issue_vectors.append(issue_vector)
        return issue_vectors