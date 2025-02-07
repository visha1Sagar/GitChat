# rank_fusion.py
from typing import List, Dict, Tuple
import pandas as pd


class RankFuser:
    def __init__(self, structured_weight: float = 0.7, semantic_weight: float = 0.3):
        self.weights = {
            'structured': structured_weight,
            'semantic': semantic_weight
        }

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to 0-1 range"""
        if not scores:
            return []
        min_score = min(scores)
        max_score = max(scores)
        return [(s - min_score) / (max_score - min_score) for s in scores] if max_score != min_score else [0.5] * len(
            scores)

    def fuse_results(self,
                     structured_results: pd.DataFrame,
                     semantic_code_results: List[Tuple[str, float]],
                     semantic_message_results: pd.DataFrame) -> List[Dict]:
        """Combine results from multiple retrieval methods"""
        fused = []

        # Structure: {type: 'commit'/'code', id: hash/filepath, score: float}

        # Add structured commit results
        if not structured_results.empty:
            structured_scores = self._normalize_scores(
                [1.0] * len(structured_results)  # Structured matches get full weight
            )
            for (_, row), score in zip(structured_results.iterrows(), structured_scores):
                fused.append({
                    'type': 'commit',
                    'id': row['hash'],
                    'score': score * self.weights['structured'],
                    'source': 'structured',
                    'data': row.to_dict()
                })

        # Add semantic code results
        code_scores = self._normalize_scores([s[1] for s in semantic_code_results])
        for (file_path, raw_score), norm_score in zip(semantic_code_results, code_scores):
            fused.append({
                'type': 'code',
                'id': file_path,
                'score': norm_score * self.weights['semantic'],
                'source': 'semantic',
                'data': {'file_path': file_path, 'similarity': raw_score}
            })

        # Add semantic message results
        if not semantic_message_results.empty:
            message_scores = self._normalize_scores(
                semantic_message_results['similarity'].tolist()
            )
            for (_, row), score in zip(semantic_message_results.iterrows(), message_scores):
                fused.append({
                    'type': 'commit',
                    'id': row['hash'],
                    'score': score * self.weights['semantic'],
                    'source': 'semantic',
                    'data': row.to_dict()
                })

        # Group and merge duplicate items
        merged = {}
        for item in fused:
            key = (item['type'], item['id'])
            if key in merged:
                merged[key]['score'] += item['score']
                merged[key]['sources'].append(item['source'])
            else:
                merged[key] = {
                    **item,
                    'sources': [item['source']]
                }

        return sorted(merged.values(), key=lambda x: x['score'], reverse=True)