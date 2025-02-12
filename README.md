# GitChat - Your Conversational Codebase Assistant 💬

[![Project Status](https://img.shields.io/badge/Status-Work%20in%20Progress-orange)](https://github.com/visha1Sagar/GitChat-System)

**GitChat** is a tool designed to help you understand and navigate codebases using natural language. Ask questions about your Git repository and receive insightful answers derived from commit history, code content, and issue tracker data. It leverages a hybrid search engine, combining structured and semantic approaches, to provide comprehensive and relevant results directly within a user-friendly chat interface.

## ✨ Key Features

*   **Natural Language Codebase Querying:** Interact with your codebase using plain English questions.
*   **Hybrid Search Engine:** Employs a combination of structured (keyword-based) and semantic (vector-based) search methodologies to ensure thorough and contextually relevant results.
*   **Semantic Understanding of Code & Commit Messages:** Utilizes advanced sentence transformer models to grasp the meaning behind your queries and codebase elements (code snippets, commit messages, issues).
*   **Git History Analysis:** Parses and analyzes Git commit history to provide context on code evolution, file changes, and author contributions.
*   **GitHub Issue Tracker Integration:** Fetches and incorporates data from GitHub Issues to provide a holistic project view, including open and closed issues.
*   **Conversation Memory & Temporal Context:** Remembers past interactions within a session and offers temporal context by highlighting recent code changes related to previous discussions.
*   **User-Friendly Gradio Interface:** Provides an intuitive web-based chat interface for easy exploration of codebases and question answering.
*   **Multiple Rank Fusion Strategies:** Integrates different rank fusion techniques (Weighted Rank, Borda Count, Reciprocal Rank) to combine search results effectively.

## 🚀 Getting Started

Follow these steps to set up and run GitChat System on your local machine.

### Prerequisites

*   **Python 3.7+**
*   **Git**
*   **GitHub Account (for Issue Tracker API)**

### Installation

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/visha1Sagar/GitChat.git] # Or your forked repository URL
    cd Gitchat # Go into the cloned directory
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate   # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **GitHub Token:**

    *   To fully utilize GitChat's features, especially issue tracking and to avoid GitHub API rate limits, a Personal Access Token is recommended.
    *   Generate a token with `repo` scope at [https://github.com/settings/tokens](https://github.com/settings/tokens).
    *   In the Gradio interface, you will be prompted to enter this token upon initialization.

### Running the Application

1.  **Navigate to the project directory:**

    ```bash
    cd Gitchat # If you are not already in the project directory
    ```

2.  **Run the Gradio application:**

    ```bash
    python app.py
    ```

3.  **Access the interface:** Open your web browser and navigate to the URL shown in the console (typically `http://127.0.0.1:7860`).

## 🧑‍💻 Usage

1.  **Repository Path:** In the Gradio interface, in the left column under "Repository Path", enter the **URL of a public GitHub repository** you wish to query (e.g., `https://github.com/huggingface/transformers`). You can use the default repository (`https://github.com/visha1Sagar/GitChat`) for initial testing.
2.  **GitHub Token:** If you have a GitHub Personal Access Token, paste it into the "GitHub Token" textbox. This is recommended for accessing issue data and to avoid rate limits.
3.  **Initialize System:** Click the "Initialize System" button. This action triggers the following:
    *   Downloads the specified Git repository to the `repo_directory` within the project.
    *   Parses the repository's commit history using `git log`.
    *   Vectorizes the codebase (code file contents) and commit messages using sentence transformer models.
    *   Fetches issue data from GitHub (if a token is provided and the repository is on GitHub).
    *   Initializes the hybrid search engine and memory modules.
    *   Monitor the "Initialization Status" textbox for any messages or errors.
4.  **Ask Questions:** In the chat interface on the right side, in the "Ask about the codebase" textbox, type your question related to the loaded repository. Examples:
    *   "What is the purpose of the `CodeMessageVectorizer` class?"
    *   "Show me commits that changed the `HybridSearchEngine` class."
    *   "Are there any open issues related to performance?"
    *   "What is GitChat?"
5.  **Click "Ask" or Press Enter:** GitChat System will process your query, retrieve relevant information, and display a formatted response in the "Conversation History" chatbot.
6.  **Advanced Options (Under Development):** The "Advanced Options" accordion currently displays search parameters (fusion method, weights, top-k).  Interactive configuration of these parameters is planned for future versions.

## 🗂️ Project Structure

```
visha1sagar-gitchat/
├── ResponseGenerator.py             # Generates natural language responses from search results
├── app.py                         # Gradio application, system initialization, and orchestration
├── requirements.txt               # Project dependencies (Python packages)
├── DataIngestion/                # Modules for data ingestion and processing
│   ├── code_message_vectorizer.py # Vectorizes code files and commit messages using sentence transformers
│   ├── git_parser_history.py    # Parses Git commit history from a repository
│   └── issue_tracker_api.py     # Fetches and processes issue data from GitHub API
├── Memory/                      # Modules for conversation memory and temporal linking
│   ├── __init__.py
│   ├── conversation_history.py  # Manages conversation history, saves/loads sessions, extracts entities
│   └── temporal_linker.py      # Provides temporal context by linking conversations to code changes over time
└── Search/                      # Modules for search functionality
    ├── __init__.py
    ├── rank_fusion.py           # Implements rank fusion techniques to combine search results
    ├── semantic_search.py        # Performs semantic (vector-based) search on code, messages, and issues
    └── structured_query.py      # Implements structured (keyword-based) search on commit metadata
```

## 🚧 Potential Improvements & Future Work

This project is actively being developed.  Here are some planned enhancements and potential areas for contribution:

*   **Integration of Large Language Models (LLMs):** Move towards a more conversational "Chat with Repo" approach by integrating LLMs to enhance natural language understanding, dialogue management, and response generation capabilities.
*   **Interactive Search Parameter Tuning:** Enable users to interactively configure search parameters (fusion methods, weights) through the Gradio interface.
*   **Advanced Code Chunking & Vectorization:** Optimize code chunking strategies and explore more advanced vectorization techniques for better code representation.
*   **Contextual Code Snippet Display:** Enhance the response generation to include relevant code snippets directly in the chat interface for code references.
*   **Persistent Data Storage:** Implement persistent storage for vectorized data, conversation history, and system state to avoid reprocessing on each application start and to support session persistence.
*   **Improved Error Handling & Rate Limit Management:** Enhance error handling throughout the system, providing more informative messages and robustly manage GitHub API rate limits (e.g., with exponential backoff, caching).
*   **Comprehensive Testing Suite:** Develop unit and integration tests to ensure system stability, correctness, and facilitate easier future development.

## 🤝 Contributing

Contributions are highly encouraged!  If you have suggestions for improvements, bug reports, or new feature ideas, please feel free to:

1.  Fork the repository on GitHub.
2.  Create a new branch dedicated to your feature or bug fix.
3.  Implement your changes.
4.  Include relevant tests to cover your changes.
5.  Submit a pull request with a clear description of your contribution.

## ✉️ Contact

[LinkedIn Profile](https://www.linkedin.com/in/vishal--sagar/)

---

**Let GitChat be your intelligent companion for codebase exploration, making code understanding more conversational and efficient!**

