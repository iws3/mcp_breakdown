import asyncio
import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.workflow import Context

# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """
You are a helpful database assistant with access to a SQLite database.
You can help users:
- Query the database to find information
- Add new records to the database
- Update or delete existing records
- Count records

When users ask questions, think about which tools to use and call them appropriately.
Always be clear about what data you're working with.

Available tools:
- add_person: Add a new person (use this for simple additions)
- read_data: Query the database (use SELECT queries)
- add_data: Execute INSERT/UPDATE/DELETE SQL
- update_person: Update existing person
- delete_person: Delete a person by ID
- count_people: Count total people

IMPORTANT:
- Use the EXACT tool names listed above.
- Do NOT append '_Schema' or any other suffix to tool names.
- For simple requests like "add a person", use add_person.
- For complex queries, use read_data with SQL.
"""

# Initialize Gemini LLM
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

llm = Gemini(
    model="models/gemini-1.5-flash",
    api_key=API_KEY,
    temperature=0.1,
)

async def get_agent(server_url: str):
    """Initialize MCP client and create agent with database tools"""
    print(f"🔌 Connecting to MCP server at {server_url}...")
    
    try:
        # Connect to HTTP MCP server
        mcp_client = BasicMCPClient(f"{server_url}/mcp")
        mcp_tool_spec = McpToolSpec(client=mcp_client)
        
        # Fetch available tools
        print("📥 Fetching tools from server...")
        tools = await mcp_tool_spec.to_tool_list_async()
        
        print(f"\n✅ Connected! Loaded {len(tools)} tools:")
        for i, tool in enumerate(tools, 1):
            # Show exact tool name for debugging
            tool_name = tool.metadata.name
            tool_desc = tool.metadata.description
            print(f"   {i}. {tool_name}")
            print(f"      → {tool_desc}")
        
        print()  # Extra newline for readability
        
        # Create agent with tools
        agent = FunctionAgent(
            name="DatabaseAgent",
            description="AI agent that helps manage and query a SQLite database",
            tools=tools,
            llm=llm,
            system_prompt=SYSTEM_PROMPT,
        )
        
        return agent
        
    except Exception as e:
        print(f"\n❌ Failed to connect to MCP server!")
        print(f"   Error: {e}")
        print(f"\n💡 Make sure your server is running:")
        print(f"   Terminal 1: python server.py")
        print(f"   Terminal 2: python gemini-client.py\n")
        raise

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = True,
):
    """Process user message through the agent"""
    if verbose:
        print(f"\n🤔 Agent thinking...\n")
    
    handler = agent.run(message_content, ctx=agent_context)
    
    # Stream events as they happen
    async for event in handler.stream_events():
        if verbose:
            if isinstance(event, ToolCall):
                print(f"🔧 Calling tool: {event.tool_name}")
                args_str = ", ".join(f"{k}={v}" for k, v in event.tool_kwargs.items())
                print(f"   With: {args_str}")
            elif isinstance(event, ToolCallResult):
                result_preview = str(event.tool_output)[:100]
                if len(str(event.tool_output)) > 100:
                    result_preview += "..."
                print(f"✅ Result: {result_preview}\n")
    
    response = await handler
    return str(response)

async def main():
    """Main interactive loop"""
    server_url = "http://127.0.0.1:8000"
    
    print("=" * 70)
    print("🚀 Database Assistant with MCP + Google Gemini")
    print("=" * 70)
    
    # Check for API key
    if not API_KEY:
        print("\n❌ Error: No API key found!")
        print("💡 Set it as environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        print("💡 Or edit API_KEY variable in the code")
        print("💡 Get your API key from: https://makersuite.google.com/app/apikey\n")
        return
    
    # Test Gemini connection
    print("\n📡 Testing Google Gemini connection...")
    try:
        test = llm.complete("Say 'ready' in one word")
        print(f"✅ Gemini ready: {test}\n")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        print("💡 Check your API key and internet connection\n")
        return
    
    # Initialize agent
    try:
        agent = await get_agent(server_url)
        agent_context = Context(agent)
    except Exception:
        return
    
    print("=" * 70)
    print("✅ Ready! Ask me anything about the database.")
    print("=" * 70)
    
    print("\n💡 Example queries:")
    print("   • Show me all people in the database")
    print("   • Add a person named John, age 30, email john@example.com")
    print("   • How many people are in the database?")
    print("   • Find people older than 25")
    print("   • Update person with ID 1, set age to 35")
    print("   • Delete person with ID 2")
    print("\n💬 Type 'exit' to quit\n")
    
    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "q", "bye"]:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process message
            response = await handle_user_message(
                user_input,
                agent,
                agent_context,
                verbose=True
            )
            
            print(f"\n🤖 Agent: {response}")
            print("\n" + "-" * 70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Try rephrasing your request or check the server connection\n")

if __name__ == "__main__":
    asyncio.run(main())