# Search/rank_fusion.py
from typing import List, Dict

class RankFusion:
    def __init__(self):
        pass

    def weighted_rank_fusion(self, structured_results: List[Dict], semantic_results: List[Dict], structured_weight: float, semantic_weight: float) -> List[Dict]:
        """Simple weighted rank fusion (as before)"""
        fused_results = []
        structured_ranked_ids = {item['id']: i for i, item in enumerate(structured_results)}
        semantic_ranked_ids = {item['id']: i for i, item in enumerate(semantic_results)}

        for item in structured_results + semantic_results: # Iterate over all items to avoid missing any
            if item not in fused_results: # Ensure no duplicates if an item appears in both lists.
                fused_results.append(item)

        for item in fused_results:
            structured_rank = structured_ranked_ids.get(item['id'], len(structured_results)) # default to last rank if not found
            semantic_rank = semantic_ranked_ids.get(item['id'], len(semantic_results)) # default to last rank if not found
            item['fusion_score'] = (structured_weight * (1 - structured_rank/len(structured_results)) if structured_results else 0) + \
                                   (semantic_weight * (1 - semantic_rank/len(semantic_results)) if semantic_results else 0)

        fused_results.sort(key=lambda x: x['fusion_score'], reverse=True)
        return fused_results

    def borda_count_fusion(self, structured_results: List[Dict], semantic_results: List[Dict]) -> List[Dict]:
        """Borda count rank fusion"""
        fused_results = []
        structured_ranked_ids = {item['id']: i for i, item in enumerate(structured_results)}
        semantic_ranked_ids = {item['id']: i for i, item in enumerate(semantic_results)}

        for item in structured_results + semantic_results: # Iterate over all items to avoid missing any
            if item not in fused_results: # Ensure no duplicates if an item appears in both lists.
                fused_results.append(item)


        for item in fused_results:
            structured_rank = structured_ranked_ids.get(item['id'], len(structured_results)) # default to last rank if not found
            semantic_rank = semantic_ranked_ids.get(item['id'], len(semantic_results)) # default to last rank if not found
            item['fusion_score'] = (len(structured_results) - structured_rank if structured_results else 0) + \
                                   (len(semantic_results) - semantic_rank if semantic_results else 0) # Borda count is rank from bottom

        fused_results.sort(key=lambda x: x['fusion_score'], reverse=True)
        return fused_results


    def reciprocal_rank_fusion(self, structured_results: List[Dict], semantic_results: List[Dict], k=60) -> List[Dict]:
        """Reciprocal rank fusion"""
        fused_results = []
        ranked_ids = {}

        for i, item in enumerate(structured_results):
            ranked_ids[item['id']] = ranked_ids.get(item['id'], 0) + 1/(k + i + 1) # Add reciprocal rank from structured

        for i, item in enumerate(semantic_results):
            ranked_ids[item['id']] = ranked_ids.get(item['id'], 0) + 1/(k + i + 1) # Add reciprocal rank from semantic


        unique_item_ids = set(ranked_ids.keys()) # Get unique IDs
        fused_results = []
        for item_id in unique_item_ids:
            # Find the original item (you might need to adjust this based on how 'item' is structured and where 'id' comes from in your original search results)
            # Assuming 'id' is unique enough to identify the item across result types.
            structured_item = next((item for item in structured_results if item['id'] == item_id), None)
            semantic_item = next((item for item in semantic_results if item['id'] == item_id), None)

            # Prioritize structured_item if available, else semantic_item. Adjust as needed.
            original_item = structured_item if structured_item else semantic_item

            if original_item: # Ensure item is found (should be unless there's an ID issue)
                fused_item = original_item.copy() # Create a copy to avoid modifying original list.
                fused_item['fusion_score'] = ranked_ids[item_id] # Assign fusion score
                fused_results.append(fused_item)


        fused_results.sort(key=lambda x: x['fusion_score'], reverse=True)
        return fused_results

    def fuse_ranks(self, structured_results: List[Dict], semantic_results: List[Dict], fusion_method: str = 'weighted', **kwargs) -> List[Dict]:
        """Main fusion dispatcher"""
        if fusion_method == 'weighted':
            return self.weighted_rank_fusion(structured_results, semantic_results, kwargs.get('structured_weight', 0.7), kwargs.get('semantic_weight', 0.3))
        elif fusion_method == 'borda':
            return self.borda_count_fusion(structured_results, semantic_results)
        elif fusion_method == 'reciprocal_rank':
            return self.reciprocal_rank_fusion(structured_results, semantic_results, kwargs.get('k', 60)) # Default k=60 from literature
        else:
            raise ValueError(f"Unknown fusion method: {fusion_method}")