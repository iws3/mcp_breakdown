# MCP Financial Analyst & Educational Agent

This project implements an **AI-Powered Financial Analyst** that combines:
1.  **CrewAI**: For orchestrating multi-agent workflows (parsing queries, writing code).
2.  **Google Gemini (2.5 Flash)**: As the intelligence engine for analysis and storytelling.
3.  **FastMCP**: To expose the tool as a Model Context Protocol (MCP) server for Claude Desktop.
4.  **Streamlit**: For a beautiful, interactive web user interface.
5.  **Pollinations AI**: For generating educational illustrations.

## Features

-   **📈 Stock Analysis**: Fetches real-time data using `yfinance`, generates Python code to visualize it, and plots trends.
-   **🌍 Village Story Mode**: Explains complex financial concepts using simple, culturally relevant African analogies (e.g., "The Village Farm").
-   **🎨 AI Illustrations**: Generates visual representations of the financial stories on the fly.
-   **🖥️ Dual Interface**: Use it via **Claude Desktop** (as a tool) or the **Streamlit Web App**.

## Prerequisites

-   Python 3.10+
-   A [Google Gemini API Key](https://ai.google.dev/)

## Installation

1.  **Clone the repository** (or navigate to this folder).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configuration**:
    Create a `.env` file in this directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

## Usage

### 1. Web Interface (Streamlit) - Recommended

The easiest way to use the agent is via the web app.

```bash
streamlit run app.py
```
-   Open your browser at `http://localhost:8501`.
-   Enter a query (e.g., "Compare Tesla and Ford").
-   Click **Analyze**.
-   Switch to the **"Village Story"** tab to get a simplified explanation with an AI image.

### 2. Claude Desktop Integration

To use this agent inside Claude Desktop:

1.  Open your Claude Desktop config file:
    -   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
    -   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
2.  Add the following configuration:

```json
{
  "mcpServers": {
    "financial-analyst": {
      "command": "path/to/your/venv/Scripts/python.exe",
      "args": [
        "path/to/your/project/4_financial_analyst_mcp/server.py"
      ],
      "env": {
        "GOOGLE_API_KEY": "your_key_here"
      }
    }
  }
}
```
*(Replace paths with your actual absolute paths)*

## Project Structure

-   `app.py`: The Streamlit web application.
-   `server.py`: The MCP server and core analysis logic (`run_analysis`, `generate_story`).
-   `finance_crew.py`: The CrewAI agent definitions (Parser & Code Writer).
-   `requirements.txt`: Python dependencies.

## Security Note

This agent **executes generated Python code** on your local machine to create plots. While useful for personal projects, be cautious when using it with untrusted inputs or in production environments.
