# ResponseGenerator.py
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
            return f"Issue #{issue_num} (not found)"

        status = "closed" if issue['closed_at'] else "open"
        date = datetime.fromisoformat(issue['created_at']).strftime("%b %Y")
        comments = f"{len(issue['comments'])} comments" if issue['comments'] else ""
        return (f"Issue #{issue_num} ({status}, {date}): {issue['title']}\n"
                f"{textwrap.shorten(issue['body'], width=100, placeholder='...')} {comments}")

    def _format_code(self, code_item: Dict) -> str:
        """Format code search result into natural language"""
        return f"File: {code_item['file_path']}\n" \
               f"Relevance: {code_item['similarity']:.2f} - Contains related code patterns"

    def _format_issue_search_result(self, issue_result: Dict) -> str: # New formatter for issue search results
        """Format issue search result from semantic search into natural language"""
        # Issue result from semantic search is currently just index and score.
        # We need to retrieve the actual issue data using the index.
        issue_index = issue_result['index']
        #  <--- Assuming you can access the original 'self.issues' list in the same order as vectors were created.
        #  This might require you to adjust how issues and issue vectors are stored and linked.
        if 0 <= issue_index < len(self.issues):
            issue = self.issues[issue_index]
            return self._format_issue(issue['number']) # Re-use _format_issue to format issue details.
        else:
            return "Related Issue Found (details not available)" # Fallback if issue not found.


    def generate_response(
            self,
            search_results: List[Dict],
            temporal_context: Optional[str] = None,
            issue_refs: List[int] = []
    ) -> str:
        """Generate natural language response from multiple sources, including issues."""
        response_parts = []

        # Add temporal context if available
        if temporal_context:
            response_parts.append(f"Context Update:\n{temporal_context}\n")
        # Process search results by type
        commits = []
        code_files = []
        semantic_issues = [] # To store semantic issue search results
        for result in search_results:
            if result['type'] == 'commit':
                commits.append(result['data'])
            elif result['type'] == 'code':
                code_files.append(result['data'])
            elif result['type'] == 'issue': # Handle issue results
                semantic_issues.append(result) # Store the entire result item, which contains index and score.


        # Add commit information
        if commits:
            response_parts.append("Relevant Commit History:")
            for commit in [commits[:3] if len(commits)>2 else commits][0]:  # Show top 3 commits if there

                response_parts.append(self._format_commit(commit))

        # Add code references
        if code_files:
            response_parts.append("\nCode References:")
            for code in code_files[:2]:  # Show top 2 code matches
                response_parts.append(self._format_code(code))

        # Add related issues (keyword-based from commit messages - as before)
        if issue_refs:
            response_parts.append("\nRelated Issues (mentioned in commits):") # Clarify source of these issues
            for issue_num in issue_refs[:3]:  # Show top 3 issues
                response_parts.append(self._format_issue(issue_num))

        # Add semantic issue search results
        if semantic_issues:
            response_parts.append("\nRelated Issues (semantically similar):") # Clarify source
            for issue_result in semantic_issues[:3]: # Show top 3 semantic issue results
                response_parts.append(self._format_issue_search_result(issue_result)) # Use new formatter


        # Add fallback if no results
        if not response_parts:
            return "I couldn't find any relevant information in the codebase history. " \
                   "This might be a recent change or require deeper code analysis."

        return "\n".join(response_parts)

    def generate_error_response(self, error: Exception) -> str:
        """Generate user-friendly error message"""
        return f"Sorry, I encountered an error: {str(error)}\n" \
               "Please try rephrasing your question or check the repository status."