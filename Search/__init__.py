from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

from Search.rank_fusion import RankFusion
from Search.semantic_search import SemanticSearchEngine
from Search.structured_query import StructuredQueryEngine


class HybridSearchEngine:
    def __init__(self, commit_df: pd.DataFrame, code_vectors: Dict[str, np.ndarray], message_vectors: np.ndarray, issue_vectors: Dict[str, np.ndarray] = None):
        self.structured_engine = StructuredQueryEngine(commit_df)
        self.semantic_engine = SemanticSearchEngine(code_vectors, message_vectors, commit_df, issue_vectors)
        self.rank_fusion = RankFusion()  # Initialize RankFusion with default weights and k

    def search(self, query: str, query_vec: np.ndarray, search_params: dict = None, top_k: int = 10) -> List[Dict]:
        if search_params is None:
            search_params = {}

        structured_results = self.structured_engine.search_commits(query)
        semantic_code = self.semantic_engine.semantic_code_search(query_vec) # Corrected method name
        semantic_messages = self.semantic_engine.semantic_commit_message_search(query_vec) # Corrected method name
        semantic_issues = self.semantic_engine.semantic_issue_search(query_vec) if self.semantic_engine.issue_vectors is not None else [] # Corrected method name

        # Convert to List[Dict] with 'id', 'data', and 'score' keys
        fused_structured = [{'id': res['hash'], 'data': res} for res in structured_results.to_dict('records')] # Convert DataFrame to list of dicts
        fused_semantic_code = [{'id': res['id'], 'data': res['data'], 'score': res['score']} for res in semantic_code] # Corrected line - use keys
        fused_semantic_messages = [{'id': res['id'], 'data': res['data'], 'score': res['score']} for res in semantic_messages] # Corrected line - use keys
        fused_semantic_issues = [{'id': res['id'], 'data': res['data'], 'score': res['score']} for res in semantic_issues] # Corrected line - use keys


        # Fuse results
        fusion_method = search_params.get('fusion_method', 'weighted')
        fused_results = self.rank_fusion.fuse_ranks(
            fused_structured,
            fused_semantic_code + fused_semantic_messages + fused_semantic_issues,
            fusion_method=fusion_method,  # Keep explicit fusion_method
            **{k: v for k, v in search_params.items() if k != 'fusion_method'}  # Exclude fusion_method from kwargs
        )

        print("fused_results : ",fused_results)

        # Extract original data and limit top-k results
        final_results = []
        for item in fused_results[:top_k]:
            final_results.append({
                'type': self._get_result_type(item['data']),  # Determine type based on data
                'data': item['data'],
                'fusion_score': item['fusion_score'],  # Use the final fused score
                'sources': item.get('sources', []) # Include source information
            })

        return final_results

    def _get_result_type(self, data: Dict) -> str:
        """Helper function to determine result type based on data."""
        if 'hash' in data and 'message' in data:  # Check if both 'hash' and 'message' are present
            return 'commit'
        elif 'file_path' in data:
            return 'code'
        elif 'number' in data:
            return 'issue'
        return 'unknown'  # Default if type cannot be determined