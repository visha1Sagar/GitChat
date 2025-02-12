# GitChat System - Your Conversational Codebase Assistant 💬

[![Project Status](https://img.shields.io/badge/Status-Work%20in%20Progress-orange)](https://github.com/your-github-username/GitChat-System) **GitChat System** is a sophisticated tool designed to help you understand and navigate codebases through natural language conversations.  Ask questions about your Git repository and get insightful answers leveraging commit history, code content, and issue tracker data.

## ✨ Key Features

*   **Natural Language Codebase Querying:** Ask questions about your codebase in plain English.
*   **Hybrid Search Engine:** Combines structured keyword search with semantic vector search for comprehensive and relevant results.
*   **Semantic Code & Commit Message Understanding:** Leverages advanced language models to understand the meaning of your queries and codebase elements.
*   **Git History Analysis:**  Extracts and analyzes commit history to provide context on code evolution and changes.
*   **Issue Tracker Integration:** Fetches and incorporates data from GitHub Issues to provide a holistic view of the project.
*   **Conversation Memory & Temporal Context:** Remembers past conversations and provides temporal context by highlighting code changes that occurred after discussions.
*   **User-Friendly Gradio Interface:**  Interactive web interface for easy codebase exploration and question answering.

## 🚀 Getting Started

Follow these steps to get GitChat System up and running on your local machine.

### Prerequisites

*   **Python 3.7+**
*   **Git**
*   **GitHub Account (optional, for Issue Tracker API)**

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-github-username/GitChat-System.git  # Replace with your repo URL
    cd GitChat
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **GitHub Token (Optional but Recommended for Issue Tracking and Rate Limits):**

    *   To enable fetching GitHub Issues and to avoid API rate limits, you may need a GitHub Personal Access Token.
    *   Generate a token with `repo` scope at [https://github.com/settings/tokens](https://github.com/settings/tokens).
    *   **Important Security Note:**  For now, you might need to temporarily paste this token into the `app.py` file (look for `self.github_token = "jfjdn"` and replace `"jfjdn"` with your token). **This is insecure for production.  Future versions will implement secure token management (e.g., environment variables).**

### Running the Application

1.  **Navigate to the project directory:**

    ```bash
    cd GitChat
    ```

2.  **Run the Gradio application:**

    ```bash
    python app/app.py
    ```

3.  **Access the interface:** Open your web browser and go to the URL shown in the console (usually `http://127.0.0.1:7860`).

## 🧑‍💻 Usage

1.  **Repository Path:** In the Gradio interface, enter the **URL of a public GitHub repository** you want to explore in the "Repository Path" textbox (e.g., `https://github.com/torvalds/linux`). You can also try with the provided default repository.
2.  **(Optional) GitHub Token:** If you have a GitHub token, paste it into the "GitHub Token" textbox.
3.  **Initialize System:** Click the "Initialize System" button. This will download the repository, parse its history, and prepare the system for querying.  Check the "Initialization Status" textbox for any messages.
4.  **Ask Questions:**  In the "Ask about the codebase" textbox, type your question about the repository (e.g., "What is the purpose of file X?", "Show me commits related to feature Y", "Are there any open issues about performance?").
5.  **Click "Ask" or press Enter:**  The GitChat System will process your query and display the response in the "Conversation History" chatbot.
6.  **Explore "Advanced Options":** (Currently, the "Advanced Options" accordion displays search parameters, but interactive configuration is not yet implemented in this version).

## 🗂️ Project Structure

```markdown
GitChat System
├── Data Ingestion Layer
│   ├── Git History Parser
│   │   └── `git_history_parser.py`  # Parses Git commit history
│   ├── Code/Message Vectorizer
│   │   └── `code_message_vectorizer.py` # Converts code and messages to vectors
│   └── Issue Tracker API
│       └── `issue_tracker_api.py` # Fetches data from GitHub Issue Tracker
├── Hybrid Search Engine
│   ├── Structured Query
│   │   └── `structured_query.py` # Keyword-based search
│   ├── Vector Semantic Search
│   │   └── `semantic_search.py`  # Vector-based semantic search
│   └── Rank Fusion
│       └── `rank_fusion.py`      # Combines search results
├── Memory Module
│   ├── Conversation History
│   │   └── `conversation_history.py` # Manages conversation history
│   └── Temporal Linker
│       └── `temporal_linker.py`    # Links conversations to temporal context
├── Response Generator
│   └── `response_generator.py`     # Generates natural language responses
├── app
│   └── `app.py`                    # Gradio application and system orchestration
├── `requirements.txt`              # Project dependencies
└── `README.md`                     # This file

```


**To use this in your `README.md` file:**

1.  Copy the entire block of text above, starting from `## 🗂️ Project Structure` to the closing backticks `` ` ``.
2.  Paste it directly into your `README.md` file where you want the project structure to appear.

This Markdown code, when rendered by GitHub or a Markdown viewer, should display the project structure in a visually clear tree-like format using Unicode characters. Let me know if you need any adjustments!


## 🚧 Potential Improvements & Future Work

This project is under active development.  Here are some planned improvements and areas for contribution:

*   **Enhanced Security:** Implement secure GitHub token management using environment variables or secure configuration.
*   **Robust Error Handling:** Improve error handling throughout the system, providing more informative error messages and logging.
*   **Rate Limit Management:** Implement strategies to handle GitHub API rate limits gracefully (e.g., exponential backoff).
*   **Scalability & Efficiency:** Optimize vectorization, semantic search, and data loading for large codebases. Consider using vector databases and indexing techniques.
*   **Interactive Search Parameter Tuning:**  Make the "Advanced Options" in the UI interactive, allowing users to adjust search weights and parameters.
*   **Enhanced Query Understanding:**  Incorporate more advanced NLP techniques for more accurate and flexible natural language query parsing.
*   **Improved Response Generation:**  Use response templates for more customizable and contextually rich answers.  Add code formatting and improve "no results" messages.
*   **Full Issue Tracker Temporal Linking:** Fully integrate issue tracker data into the temporal linking module to provide context on issue updates and discussions over time.
*   **Clear Conversation History Feature:** Add a button to clear the conversation history in the UI.
*   **Persistent Data Storage:** Implement persistent storage for vectorized data and conversation history to avoid re-processing on each startup.
*   **More Comprehensive Testing:** Add unit and integration tests to ensure system stability and correctness.

## 🤝 Contributing

Contributions are welcome!  If you have ideas for improvements, bug fixes, or new features, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or fix.
3.  Make your changes and commit them.
4.  Submit a pull request.

Please follow coding style conventions and include relevant tests when contributing.


## ✉️ Contact

[LinkedIn] (https://www.linkedin.com/in/vishal--sagar/)

---

**Let GitChat be your guide to understanding code, one question at a time!**