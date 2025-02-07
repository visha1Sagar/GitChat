# semantic_search.py
import numpy as np
from typing import Dict, List, Tuple

import pandas as pd
from sentence_transformers import util


class SemanticSearchEngine:
    def __init__(self,
                 code_vectors: Dict[str, np.ndarray],
                 message_vectors: np.ndarray,
                 commit_df: pd.DataFrame):
        self.code_vectors = code_vectors
        self.message_vectors = message_vectors
        self.commit_df = commit_df

    def _cosine_similarity(self, query_vec: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """Compute cosine similarities between query and vectors"""
        return util.cos_sim(query_vec, vectors).numpy().flatten()

    def search_code(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """Semantic search across codebase"""
        results = []
        for file_path, chunks in self.code_vectors.items():
            similarities = self._cosine_similarity(query_vec, chunks)
            max_score = np.max(similarities)
            results.append((file_path, max_score))

        return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

    def search_messages(self, query_vec: np.ndarray, top_k: int = 5) -> pd.DataFrame:
        """Semantic search across commit messages"""
        similarities = self._cosine_similarity(query_vec, self.message_vectors)
        scored_df = self.commit_df.assign(similarity=similarities)
        return scored_df.sort_values('similarity', ascending=False).head(top_k)