# server.py
import sqlite3
from fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("MCP TOOLS SERVER")

# Initialize database
def init_db():
    """Create the people table if it doesn't exist"""
    conn = sqlite3.connect("data.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized")

@mcp.tool()
def add_data(query: str) -> str:
    """Execute an INSERT/UPDATE/DELETE query on the database"""
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.execute(query)
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return f"Success! {rows_affected} row(s) affected."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_data(query: str = "SELECT * FROM people") -> str:
    """Execute a SELECT query and return results"""
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.execute(query)
        results = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        if not results:
            return "No data found."
        
        # Format results nicely
        formatted = f"Columns: {', '.join(columns)}\n\n"
        for row in results:
            formatted += f"{row}\n"
        
        return formatted
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def add_person(name: str, age: int, email: str) -> str:
    """Add a new person to the database (easier than writing SQL)"""
    try:
        conn = sqlite3.connect("data.db")
        conn.execute(
            "INSERT INTO people (name, age, email) VALUES (?, ?, ?)",
            (name, age, email)
        )
        conn.commit()
        conn.close()
        return f"✅ Added {name} to database!"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def update_person(person_id: int, name: str = None, age: int = None, email: str = None) -> str:
    """Update an existing person's information"""
    try:
        conn = sqlite3.connect("data.db")
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if age is not None:
            updates.append("age = ?")
            params.append(age)
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if not updates:
            return "No updates provided"
        
        params.append(person_id)
        query = f"UPDATE people SET {', '.join(updates)} WHERE id = ?"
        cursor = conn.execute(query, params)
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            return f"✅ Updated person with ID {person_id}"
        else:
            return f"No person found with ID {person_id}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def delete_person(person_id: int) -> str:
    """Delete a person from the database by their ID"""
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.execute("DELETE FROM people WHERE id = ?", (person_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        if rows_affected > 0:
            return f"✅ Deleted person with ID {person_id}"
        else:
            return f"No person found with ID {person_id}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def count_people() -> str:
    """Count the total number of people in the database"""
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.execute("SELECT COUNT(*) FROM people")
        count = cursor.fetchone()[0]
        conn.close()
        return f"Total people in database: {count}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    print("=" * 70)
    print("🚀 Starting MCP Tools Server on http://127.0.0.1:8000")
    print("=" * 70)
    print("\nAvailable tools:")
    print("  • add_data(query) - Execute SQL INSERT/UPDATE/DELETE")
    print("  • read_data(query) - Execute SQL SELECT")
    print("  • add_person(name, age, email) - Add person easily")
    print("  • update_person(person_id, name, age, email) - Update person")
    print("  • delete_person(person_id) - Delete person by ID")
    print("  • count_people() - Count total people")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 70)
    
    # Run with HTTP transport
    mcp.run(transport="http", host="127.0.0.1", port=8000)