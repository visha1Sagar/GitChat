# app.py
import gradio as gr
import os
from DataIngestion.code_message_vectorizer import CodeMessageVectorizer
from DataIngestion.issue_tracker_api import IssueTrackerAPI
from DataIngestion.git_parser_history import GitHistoryParser
import github
import git
from Search import HybridSearchEngine
from Memory import MemoryModule
from ResponseGenerator import ResponseGenerator
from typing import List, Dict
import re
import os
import shutil
import stat


class GitChatSystem:
    def __init__(self, repo_path: str = ".", github_token: str = None):
        self.repo_path = repo_path
        self.repo = None
        self.github_token = ""
        self.initialized = False
        self.conversation_history = []
        print(f"Initialized GitChatSystem with repo_path: {repo_path} and github_token: {github_token}")

    def initialize_system(self, github_token: str):
        """Initialize all components with current repo state"""
        try:
            self.github_token = github_token
            print("Initializing system...")
            # DataIngestion
            if self.repo is not None:
                self.git_parser = GitHistoryParser(repo=self.repo)
                print("Using existing repo for GitHistoryParser")
            else:
                self.git_parser = GitHistoryParser(repo_url=self.repo_path)
                print(f"Using repo_url: {self.repo_path} for GitHistoryParser")

            self.commit_df = self.git_parser.parse_commit_history()
            print(f"Parsed commit history: {self.commit_df}")

            self.vectorizer = CodeMessageVectorizer()
            self.code_vectors = self.vectorizer.vectorize_codebase(self.repo_path)
            print(f"Vectorized codebase: {self.code_vectors}")

            self.message_vectors = self.vectorizer.vectorize_commit_messages(
                self.commit_df["message"].tolist()
            )
            print(f"Vectorized commit messages: {self.message_vectors}")

            self.issue_tracker = IssueTrackerAPI(self.github_token)
            repo_name = self._extract_repo_name()
            print(f"Extracted repo name: {repo_name}")
            self.issues = self.issue_tracker.fetch_repo_issues(repo_name)
            print(f"Fetched repo issues: {self.issues}")
            issue_vectors_for_search = [issue['vector'] for issue in self.issues] if self.issues else None
            print(f"Issue vectors for search: {issue_vectors_for_search}")

            # Search Engine
            self.search_engine = HybridSearchEngine(
                self.commit_df, self.code_vectors, self.message_vectors, issue_vectors=issue_vectors_for_search
            )
            print("Initialized HybridSearchEngine")

            # Memory and Response
            self.memory = MemoryModule(self.commit_df)
            self.response_gen = ResponseGenerator(self.issues)
            print("Initialized MemoryModule and ResponseGenerator")

            self.initialized = True
            print("System initialized successfully!")
            return "System initialized successfully!"
        except Exception as e:
            print(f"Initialization failed: {str(e)}")
            return f"Initialization failed: {str(e)}"

    def download_repo(self, repo_url: str):
        """Download a GitHub repository to local disk"""
        print(f"Downloading repository from URL: {repo_url}")
        if repo_url[-4:] != ".git":
            repo_url += ".git"

        if os.path.exists("repo_directory"):
            def remove_readonly(func, path, _):
                os.chmod(path, stat.S_IWRITE)
                func(path)
            shutil.rmtree("repo_directory", onerror=remove_readonly)
            print("Cleared existing repo_directory")

        try:
            self.repo = git.Repo.clone_from(repo_url, "repo_directory")
            print(f"Cloned repository to repo_directory")

            self.repo_path = os.path.join(os.getcwd(), "repo_directory")
            print(f"Set repo_path to: {self.repo_path}")
            return "Repository downloaded successfully!"
        except Exception as e:
            print(f"Repository download failed: {str(e)}")
            return f"Repository download failed: {str(e)}"

    def _extract_repo_name(self) -> str:
        """Convert local path to github repo name format"""
        if not os.path.exists("repo_directory"):
            raise ValueError("Not a valid Git repository")

        remote_url = self.repo.remotes[0].config_reader.get("url")
        print(f"Extracted remote URL: {remote_url}")
        return remote_url.replace(".git", "").split("github.com/")[-1]

    def ask_question(self, query: str):
        """Main processing pipeline"""
        if not self.initialized:
            print("System not initialized!")
            #     {"role": "assistant", "content": error_response}
            return self.conversation_history, "System not initialized!"
        try:
            print(f"Processing query: {query}")
            query_vec = self.vectorizer.model.encode([query])[0]
            print(f"Encoded query vector: {query_vec}")

            search_results = self.search_engine.search(query, query_vec, search_params={
                'fusion_method': 'reciprocal_rank',
                'structured_weight': 0.6,
                'semantic_weight': 0.4,
                'top_k': 10
            })
            print(f"Search results: {search_results}")

            temporal_context = self.memory.get_context()
            print(f"Temporal context: {temporal_context}")

            issue_refs = self._find_related_issues(search_results)
            print(f"Related issues: {issue_refs}")

            response = self.response_gen.generate_response(
                search_results, temporal_context, issue_refs
            )
            print(f"Generated response: {response}")

            self.memory.add_conversation(query, response)
            print("Updated memory with new conversation")

            response = str(response)
            self.conversation_history.extend([
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ])
            print(f"Updated conversation history: {self.conversation_history}")

            return self.conversation_history, ""
        except Exception as e:
            print(f"Error: {e}")
            error_response = self.response_gen.generate_error_response(e)
            self.conversation_history.append({"role": "assistant", "content": error_response})
            return self.conversation_history, ""

    def _find_related_issues(self, search_results: List[Dict]) -> List[int]:
        """Extract issue numbers from search results"""
        issue_numbers = set()
        for result in search_results:
            if result['type'] == 'commit':
                message = result['data'].get('message', '')
                issue_numbers.update(re.findall(r"#(\d+)", message))
        print(f"Extracted issue numbers: {issue_numbers}")
        return list(issue_numbers)[:3]

# Gradio Interface (no major changes needed right now)
def create_interface():
    system = GitChatSystem()

    with gr.Blocks(title="GitChat Codebase QA", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🗨️ GitChat - Codebase Assistant")

        with gr.Row():
            with gr.Column(scale=1):
                repo_path = gr.Textbox(label="Repository Path", value="https://github.com/visha1Sagar/GitChat")
                github_token = gr.Textbox(label="GitHub Token find at https://github.com/settings/tokens/", type="password")
                init_btn = gr.Button("Initialize System")
                init_status = gr.Textbox(label="Initialization Status", interactive=False)

            with gr.Column(scale=2):
                chat = gr.Chatbot(label="Conversation History", height=400, type='messages')
                query = gr.Textbox(label="Ask about the codebase")
                submit_btn = gr.Button("Ask")

        with gr.Accordion("Advanced Options", open=False):
            gr.Markdown("Configure search parameters:")
            search_params = gr.JSON(value={
                "fusion_method": "reciprocal_rank", # Default to reciprocal_rank now. Can change in UI later.
                "structured_weight": 0.6, # Example weights for reciprocal rank might not be as relevant, adjust if using weighted.
                "semantic_weight": 0.4,
                "top_k": 10
            })

        # Event handlers
        init_btn.click(
            fn=lambda rp, gt: (system.download_repo(rp), system.initialize_system(gt)),
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