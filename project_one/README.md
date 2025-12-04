# SQLite MCP Agent

This project demonstrates a Model Context Protocol (MCP) implementation using a SQLite database server and a Gemini-powered client agent.

## Project Structure

<img width="821" height="606" alt="image" src="https://github.com/user-attachments/assets/05737c46-7616-4bde-ad40-febdbc937759" />



- `sqlite_server.py`: An MCP server that exposes tools to interact with a SQLite database (`data.db`).
- `gemini_client.py`: An AI agent using Google's Gemini 1.5 Flash model that connects to the MCP server to perform database operations.
- `data.db`: The SQLite database file (created automatically).
- `.env`: Configuration file for API keys (not committed).

## Prerequisites

- Python 3.10+
- A Google Cloud API Key for Gemini 🤗

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Create a `.env` file in the project root:
    ```env
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

## Usage

1.  **Start the MCP Server**:
    Open a terminal and run:
    ```bash
    python sqlite_server.py
    ```
    This will start the server on `http://127.0.0.1:8000`.

2.  **Run the Client Agent**:
    Open a second terminal and run:
    ```bash
    python gemini_client.py
    ```

3.  **Interact**:
    You can now chat with the agent to manage the database.
    Examples:
    - "Add a person named Alice, age 25, email alice@example.com"
    - "Show me all people"
    - "Count the people in the database"
    - "Delete the person with ID 1"

## Tools Available

The MCP server exposes the following tools to the agent:
- `add_person`: Add a new person record.
- `read_data`: Execute SQL SELECT queries.
- `add_data`: Execute SQL INSERT/UPDATE/DELETE queries.
- `update_person`: Update an existing person's details.
- `delete_person`: Delete a person by ID.
- `count_people`: Get the total count of records.
