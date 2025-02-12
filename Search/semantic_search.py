# semantic_search.py
from typing import Dict, List
import numpy as np
import faiss
import pandas as pd # Import pandas

class SemanticSearchEngine:
    def __init__(self, code_vectors: Dict[str, np.ndarray], message_vectors: np.ndarray, commit_df: pd.DataFrame, issue_vectors=None): # Add commit_df to constructor
        self.code_vectors = self._build_faiss_index(code_vectors)
        self.message_vectors = self._build_faiss_index_messages(message_vectors)
        self.issue_vectors = self._build_faiss_index_issues(issue_vectors) if issue_vectors is not None else None
        self.commit_df = commit_df # Store commit_df

    def _build_faiss_index(self, code_vectors: Dict[str, np.ndarray]):
        index = faiss.IndexFlatIP(768)
        file_paths = []
        all_vectors = []
        for file_path, vectors in code_vectors.items():
            for vector_chunk in vectors:
                all_vectors.append(vector_chunk)
                file_paths.append(file_path)

        if all_vectors:
            index.add(np.array(all_vectors))
        return {'index': index, 'file_paths': file_paths}

    def _build_faiss_index_messages(self, message_vectors: np.ndarray):
        index = faiss.IndexFlatIP(768)
        if message_vectors.size > 0:
            index.add(message_vectors)
        return index

    def _build_faiss_index_issues(self, issue_vectors):
        index = faiss.IndexFlatIP(768)
        if issue_vectors is not None and len(issue_vectors) > 0:
            index.add(np.array(issue_vectors))
        return index

    def semantic_code_search(self, query_vector: np.ndarray, top_k=5) -> List[Dict]:
        if not self.code_vectors['index'].ntotal:
            return []

        D, I = self.code_vectors['index'].search(np.expand_dims(query_vector, axis=0), top_k)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx != -1:
                file_path = self.code_vectors['file_paths'][idx]
                results.append({
                    'id': file_path,
                    'data': {'file_path': file_path, 'similarity': score},
                    'score': score
                })
        return results

    def semantic_commit_message_search(self, query_vector: np.ndarray, top_k=5) -> List[Dict]:
        if not self.message_vectors.ntotal:
            return []

        D, I = self.message_vectors.search(np.expand_dims(query_vector, axis=0), top_k)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx != -1:
                # Now self.commit_df is correctly initialized and accessible
                commit_data = self.commit_df.iloc[idx].to_dict() if hasattr(self, 'commit_df') and not self.commit_df.empty and idx < len(self.commit_df) else {}
                results.append({
                    'id': str(idx),
                    'data': commit_data,
                    'score': score
                })
        return results

    def semantic_issue_search(self, query_vector: np.ndarray, top_k=5) -> List[Dict]:
        if self.issue_vectors is None or not self.issue_vectors.ntotal:
            return []

        D, I = self.issue_vectors.search(np.expand_dims(query_vector, axis=0), top_k)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx != -1:
                issue_data = {} # Placeholder - You'll need to link back to issue data properly
                results.append({
                    'id': str(idx),
                    'data': issue_data,
                    'score': score
                })
        return results