# app.py
import gradio as gr
import os
from DataIngestion.code_message_vectorizer import CodeMessageVectorizer
from DataIngestion.issue_tracker_api import IssueTrackerAPI

from DataIngestion.git_parser_history import GitHistoryParser
import github
import pygit
from Search import HybridSearchEngine
from Memory import MemoryModule
from ResponseGenerator import ResponseGenerator
from typing import List, Dict
import re


class GitChatSystem:
    def __init__(self, repo_path: str = ".", github_token: str = None):
        self.repo_path = repo_path
        self.github_token = github_token
        self.initialized = False
        self.conversation_history = []

    def initialize_system(self):
        """Initialize all components with current repo state"""
        try:
            # DataIngestion
            self.git_parser = GitHistoryParser(self.repo_path)
            self.commit_df = self.git_parser.parse_commit_history()

            self.vectorizer = CodeMessageVectorizer()
            self.code_vectors = self.vectorizer.vectorize_codebase(self.repo_path)
            self.message_vectors = self.vectorizer.vectorize_commit_messages(
                self.commit_df["message"].tolist()
            )

            self.issue_tracker = IssueTrackerAPI(self.github_token)
            repo_name = self._extract_repo_name()
            self.issues = self.issue_tracker.fetch_repo_issues(repo_name)

            # Search Engine
            self.search_engine = HybridSearchEngine(
                self.commit_df, self.code_vectors, self.message_vectors
            )

            # Memory and Response
            self.memory = MemoryModule(self.commit_df)
            self.response_gen = ResponseGenerator(self.issues)

            self.initialized = True
            return "System initialized successfully!"
        except Exception as e:
            return f"Initialization failed: {str(e)}"

    def _extract_repo_name(self) -> str:
        """Convert local path to github repo name format"""
        if not os.path.isdir(os.path.join(self.repo_path, ".git")):
            raise ValueError("Not a valid Git repository")

        # remote_url = git.Repo(self.repo_path).remotes[0].config_reader.get("url")
        remote_url = pygit.load(self.repo_path).remotes[0].config_reader.get("url")
        return remote_url.replace(".git", "").split("github.com/")[-1]

    def ask_question(self, query: str):
        """Main processing pipeline"""
        if not self.initialized:
            return "System not initialized!", ""

        try:
            # Process query
            query_vec = self.vectorizer.model.encode([query])[0]

            # Search
            search_results = self.search_engine.search(query, query_vec)

            # Get temporal context
            temporal_context = self.memory.get_context()

            # Find related issues
            issue_refs = self._find_related_issues(search_results)

            # Generate response
            response = self.response_gen.generate_response(
                search_results, temporal_context, issue_refs
            )

            # Update memory
            self.memory.add_conversation(query, response)

            # Format conversation history
            self.conversation_history.append((query, response))
            history_md = self._format_history_markdown()

            return response, history_md
        except Exception as e:
            return self.response_gen.generate_error_response(e), ""

    def _find_related_issues(self, search_results: List[Dict]) -> List[int]:
        """Extract issue numbers from search results"""
        issue_numbers = set()
        for result in search_results:
            if result['type'] == 'commit':
                message = result['data'].get('message', '')
                issue_numbers.update(re.findall(r"#(\d+)", message))
        return list(issue_numbers)[:3]  # Return top 3 matches

    def _format_history_markdown(self) -> str:
        """Format conversation history for display"""
        md = []
        for i, (query, response) in enumerate(self.conversation_history[-5:]):  # Last 5 exchanges
            md.append(f"**Q{i + 1}:** {query}  \n**A{i + 1}:** {response}\n")
        return "\n".join(md)


# Gradio Interface
def create_interface():
    system = GitChatSystem()

    with gr.Blocks(title="GitChat Codebase QA", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🗨️ GitChat - Codebase Assistant")

        with gr.Row():
            with gr.Column(scale=1):
                repo_path = gr.Textbox(label="Repository Path", value=".")
                github_token = gr.Textbox(label="GitHub Token (optional)", type="password")
                init_btn = gr.Button("Initialize System")
                init_status = gr.Textbox(label="Initialization Status", interactive=False)

            with gr.Column(scale=2):
                chat = gr.Chatbot(label="Conversation History", height=400)
                query = gr.Textbox(label="Ask about the codebase")
                submit_btn = gr.Button("Ask")

        with gr.Accordion("Advanced Options", open=False):
            gr.Markdown("Configure search parameters:")
            search_params = gr.JSON(value={
                "structured_weight": 0.7,
                "semantic_weight": 0.3,
                "top_k": 10
            })

        # Event handlers
        init_btn.click(
            fn=lambda rp, gt: system.initialize_system(rp, gt),
            inputs=[repo_path, github_token],
            outputs=init_status
        )

        submit_btn.click(
            fn=system.ask_question,
            inputs=query,
            outputs=[chat, query]
        )

        query.submit(
            fn=system.ask_question,
            inputs=query,
            outputs=[chat, query]
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()