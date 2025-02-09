from typing import Dict, List
import pandas as pd
from Search.rank_fusion import RankFuser
from Search.semantic_search import SemanticSearchEngine
from Search.structured_query import StructuredQueryEngine
import numpy as np

class HybridSearchEngine:
    def __init__(self,
                 commit_df: pd.DataFrame,
                 code_vectors: Dict[str, np.ndarray],
                 message_vectors: np.ndarray):
        self.structured_engine = StructuredQueryEngine(commit_df)
        self.semantic_engine = SemanticSearchEngine(code_vectors, message_vectors, commit_df)
        self.rank_fuser = RankFuser()

    def search(self, query: str, query_vec: np.ndarray, top_k: int = 10) -> List[Dict]:
        # Structured search
        structured_results = self.structured_engine.search_commits(query)
        # Semantic search
        semantic_code = self.semantic_engine.search_code(query_vec)
        semantic_messages = self.semantic_engine.search_messages(query_vec)

        # Rank fusion
        fused_results = self.rank_fuser.fuse_results(
            structured_results,
            semantic_code,
            semantic_messages
        )

        return fused_results[:top_k]