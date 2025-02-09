# response_generator.py
from typing import List, Dict, Optional
import textwrap
from datetime import datetime


class ResponseGenerator:
    def __init__(self, issue_data: List[Dict]):
        self.issue_map = {issue['number']: issue for issue in issue_data}

    def _format_commit(self, commit: Dict) -> str:
        """Format commit information into natural language"""
        date = commit['date'].to_pydatetime().strftime("%b %Y")
        files = ", ".join(commit['files_changed'][:3])
        message = textwrap.shorten(commit['message'], width=120, placeholder="...")
        return (f"Commit {commit['hash'][:6]} ({date}, {commit['author']}) - {message}\n"
                f"Files: {files}")

    def _format_issue(self, issue_num: int) -> str:
        """Format issue information into natural language"""
        issue = self.issue_map.get(issue_num)
        if not issue:
            return f"Issue #${issue_num} (not found)"

        status = "closed" if issue['closed_at'] else "open"
        date = datetime.fromisoformat(issue['created_at']).strftime("%b %Y")
        comments = f"{len(issue['comments'])} comments" if issue['comments'] else ""
        return (f"Issue #{issue_num} ({status}, {date}): {issue['title']}\n"
                f"{textwrap.shorten(issue['body'], width=100, placeholder='...')} {comments}")

    def _format_code(self, code_item: Dict) -> str:
        """Format code search result into natural language"""
        return f"File: {code_item['file_path']}\n" \
               f"Relevance: {code_item['similarity']:.2f} - Contains related code patterns"

    def generate_response(
            self,
            search_results: List[Dict],
            temporal_context: Optional[str] = None,
            issue_refs: List[int] = []
    ) -> str:
        """Generate natural language response from multiple sources"""
        response_parts = []

        # Add temporal context if available
        if temporal_context:
            response_parts.append(f"Context Update:\n{temporal_context}\n")
        # Process search results by type
        commits = []
        code_files = []
        for result in search_results:
            if result['type'] == 'commit':
                commits.append(result['data'])
            elif result['type'] == 'code':
                code_files.append(result['data'])

        # Add commit information
        if commits:
            response_parts.append("Relevant Commit History:")
            for commit in [commits[:3] if len(commits)>2 else commits][0]:  # Show top 3 commits
                response_parts.append(self._format_commit(commit))

        # Add code references
        if code_files:
            response_parts.append("\nCode References:")
            for code in code_files[:2]:  # Show top 2 code matches
                response_parts.append(self._format_code(code))

        # Add related issues
        if issue_refs:
            response_parts.append("\nRelated Issues:")
            for issue_num in issue_refs[:3]:  # Show top 3 issues
                response_parts.append(self._format_issue(issue_num))

        # Add fallback if no results
        if not response_parts:
            return "I couldn't find any relevant information in the codebase history. " \
                   "This might be a recent change or require deeper code analysis."

        return "\n".join(response_parts)

    def generate_error_response(self, error: Exception) -> str:
        """Generate user-friendly error message"""
        return f"Sorry, I encountered an error: {str(error)}\n" \
               "Please try rephrasing your question or check the repository status."