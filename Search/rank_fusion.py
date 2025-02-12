from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

# Search/rank_fusion.py 
class RankFusion:
    def __init__(self, structured_weight: float = 0.7, semantic_weight: float = 0.3, k: int = 60):
        self.structured_weight = structured_weight
        self.semantic_weight = semantic_weight
        self.k = k

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        return [(s - min_score) / (max_score - min_score) if max_score != min_score else 0.5 for s in scores] if scores else []

    def weighted_rank_fusion(self, structured_results: List[Dict], semantic_results: List[Dict]) -> List[Dict]:
        """Score-based weighted rank fusion with normalization."""
        fused_results = []

        # Normalize scores (assuming 'score' key exists)
        structured_results = [{'id': item['id'], 'score': 1.0, 'data': item['data']} for item in structured_results]
        semantic_results = [{'id': item['id'], 'score': item.get('score', 0.0), 'data': item['data']} for item in semantic_results]

        structured_scores = self._normalize_scores([item['score'] for item in structured_results])
        semantic_scores = self._normalize_scores([item['score'] for item in semantic_results])

        for item, score in zip(structured_results, structured_scores):
            fused_results.append({'id': item['id'], 'data': item['data'], 'score': score * self.structured_weight, 'source': 'structured'})
        for item, score in zip(semantic_results, semantic_scores):
            fused_results.append({'id': item['id'], 'data': item['data'], 'score': score * self.semantic_weight, 'source': 'semantic'})

        # Group and merge duplicate items
        merged = {}
        for item in fused_results:
            key = item['id']
            if key in merged:
                merged[key]['score'] += item['score']
                merged[key]['sources'].append(item['source'])
            else:
                merged[key] = {**item, 'sources': [item['source']]}

        return sorted(merged.values(), key=lambda x: x['score'], reverse=True)

    def borda_count_fusion(self, structured_results: List[Dict], semantic_results: List[Dict]) -> List[Dict]:
        # ... (Borda Count implementation - can remain largely the same)
        # However, ensure the input is List[Dict] with 'id' keys.
        fused_results = []
        structured_ranked_ids = {item['id']: i for i, item in enumerate(structured_results)}
        semantic_ranked_ids = {item['id']: i for i, item in enumerate(semantic_results)}

        for item in structured_results + semantic_results:  # Iterate over all items to avoid missing any
            if item not in fused_results:  # Ensure no duplicates if an item appears in both lists.
                fused_results.append(item)

        for item in fused_results:
            structured_rank = structured_ranked_ids.get(item['id'], len(structured_results))  # default to last rank if not found
            semantic_rank = semantic_ranked_ids.get(item['id'], len(semantic_results))  # default to last rank if not found
            item['fusion_score'] = (len(structured_results) - structured_rank if structured_results else 0) + \
                                  (len(semantic_results) - semantic_rank if semantic_results else 0)  # Borda count is rank from bottom

        fused_results.sort(key=lambda x: x['fusion_score'], reverse=True)
        return fused_results

    def reciprocal_rank_fusion(self, structured_results: List[Dict], semantic_results: List[Dict]) -> List[Dict]:
        fused_results = []
        ranked_ids = {}

        for i, item in enumerate(structured_results):
            ranked_ids[item['id']] = ranked_ids.get(item['id'], 0) + 1 / (self.k + i + 1)  # Add reciprocal rank from structured

        for i, item in enumerate(semantic_results):
            ranked_ids[item['id']] = ranked_ids.get(item['id'], 0) + 1 / (self.k + i + 1)  # Add reciprocal rank from semantic

        unique_item_ids = set(ranked_ids.keys())  # Get unique IDs
        fused_results = []
        for item_id in unique_item_ids:
            # Find the original item (you might need to adjust this based on how 'item' is structured and where 'id' comes from in your original search results)
            # Assuming 'id' is unique enough to identify the item across result types.
            structured_item = next((item for item in structured_results if item['id'] == item_id), None)
            semantic_item = next((item for item in semantic_results if item['id'] == item_id), None)

            # Prioritize structured_item if available, else semantic_item. Adjust as needed.
            original_item = structured_item if structured_item else semantic_item

            if original_item:  # Ensure item is found (should be unless there's an ID issue)
                fused_item = original_item.copy()  # Create a copy to avoid modifying original list.
                fused_item['fusion_score'] = ranked_ids[item_id]  # Assign fusion score
                fused_results.append(fused_item)

        fused_results.sort(key=lambda x: x['fusion_score'], reverse=True)
        return fused_results

    def fuse_ranks(self, structured_results: List[Dict], semantic_results: List[Dict], fusion_method: str = 'weighted', **kwargs) -> List[Dict]:
        if fusion_method == 'weighted':
            return self.weighted_rank_fusion(structured_results, semantic_results)  # No need to pass weights separately
        elif fusion_method == 'borda':
            return self.borda_count_fusion(structured_results, semantic_results)
        elif fusion_method == 'reciprocal_rank':
            return self.reciprocal_rank_fusion(structured_results, semantic_results)
        else:
            raise ValueError(f"Unknown fusion method: {fusion_method}")