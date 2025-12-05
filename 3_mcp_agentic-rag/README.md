# MCP Agentic RAG

This project implements an **Agentic RAG (Retrieval-Augmented Generation) System** exposed as an **MCP (Model Context Protocol) Server**.

It allows AI agents (like Claude Desktop or Gemini) to:
1.  **Retrieve Knowledge**: Search a local Vector Database (Qdrant) for specific domain knowledge (currently seeded with Machine Learning FAQs).
2.  **Search the Web**: Fallback to Google Search (via SerpAPI) for real-time or general information.

## Features

-   **FastMCP Server**: Built with `fastmcp` for easy tool exposure.
-   **Vector Database**: Uses `qdrant-client` for semantic search.
-   **Embeddings**: Uses `sentence-transformers` (all-MiniLM-L6-v2) for local embedding generation.
-   **Web Search**: Integrates `serpapi` for Google Search results.
-   **Claude Desktop Compatible**: Runs over `stdio` for seamless integration.
-   **Custom Client**: Includes a `client.py` to run the agent with Google Gemini if you don't use Claude.

## Prerequisites

-   Python 3.10+
-   A [SerpAPI](https://serpapi.com/) Key
-   A [Google Gemini](https://ai.google.dev/) Key (optional, for `client.py`)

## Installation

1.  **Clone the repository** (or navigate to the folder).
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Create a `.env` file in the root directory:

```env
# Required for Web Search
SERPAPI_API_KEY=your_serpapi_key_here

# Required only if using client.py (Gemini)
GOOGLE_API_KEY=your_gemini_key_here
```

## Usage

### 1. With Claude Desktop (Recommended)

To use this server with Claude Desktop, add the following to your config file:
-   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
-   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agentic-rag": {
      "command": "path/to/your/venv/Scripts/python.exe",
      "args": [
        "path/to/your/project/server.py"
      ],
      "env": {
        "SERPAPI_API_KEY": "your_key_here"
      }
    }
  }
}
```
*Note: Use absolute paths for python.exe and server.py.*

### 2. Standalone Client (Gemini)

You can run the included client script to chat with the agent using Google Gemini:

```bash
python client.py
```

### 3. Manual Server Run

To run the server manually (it uses stdio transport):

```bash
python server.py
```

## Project Structure

-   `server.py`: The main MCP server defining tools (`machine_learning_faq_retrieval_tool`, `serpapi_web_search_tool`).
-   `rag_app.py`: Handles the RAG logic (Qdrant DB, Embeddings).
-   `client.py`: A demo client using Gemini.
-   `requirements.txt`: Python dependencies.
