# structured_query.py
import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Union


class StructuredQueryEngine:
    def __init__(self, commit_df: pd.DataFrame):
        self.df = commit_df
        self.df['files_changed'] = self.df['files_changed'].apply(
            lambda x: x if isinstance(x, list) else []
        )

    def _parse_date_filter(self, query: str) -> Dict:
        """Extract date range filters from natural language query"""
        date_pattern = r"(after|before|since|until)\s+(\d{4}-\d{2}-\d{2})"
        matches = re.findall(date_pattern, query, flags=re.IGNORECASE)

        date_filters = {}
        for operator, date_str in matches:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if operator.lower() in ["after", "since"]:
                date_filters["date_lower"] = date
            elif operator.lower() in ["before", "until"]:
                date_filters["date_upper"] = date

        return date_filters

    def search_commits(self, query: str) -> pd.DataFrame:
        """Execute SQL-like queries on commit history"""
        # Extract file mentions
        file_matches = re.findall(r"\b(\w+\.\w{2,4})\b", query)

        # Build base query
        conditions = []
        if file_matches:
            file_condition = " | ".join([f"'{f}' in files_changed" for f in file_matches])
            conditions.append(f"({file_condition})")

        # Add date filters
        date_filters = self._parse_date_filter(query)
        if date_filters.get("date_lower"):
            conditions.append(f"date >= '{date_filters['date_lower']}'")
        if date_filters.get("date_upper"):
            conditions.append(f"date <= '{date_filters['date_upper']}'")

        # Combine conditions
        full_query = " & ".join(conditions) if conditions else ""
        return self.df.query(full_query) if full_query else self.df.copy()