import os
print("Client script started...")
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from server import mcp

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)

# Define tools for Gemini
retrieval_tool = FunctionDeclaration(
    name="machine_learning_faq_retrieval_tool",
    description="Retrieves relevant documents from ML FAQ. Use when user asks about Machine Learning.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The user query"
            }
        },
        "required": ["query"]
    }
)

search_tool = FunctionDeclaration(
    name="serpapi_web_search_tool",
    description="Search for information using SerpAPI (Google Search). Use for general queries not covered by FAQ.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            }
        },
        "required": ["query"]
    }
)

tools = Tool(function_declarations=[retrieval_tool, search_tool])

# Using the requested model with system instruction
model = genai.GenerativeModel(
    'gemini-2.5-flash', 
    tools=[tools],
    system_instruction="You are a helpful assistant. Use the provided tools to answer user questions. When a tool returns information, use it to construct your response. Do not call the same tool with the same arguments multiple times in a row."
)

from server import machine_learning_faq_retrieval_tool, serpapi_web_search_tool

# Manual tool mapping since we are importing the server code directly
TOOL_MAPPING = {
    "machine_learning_faq_retrieval_tool": machine_learning_faq_retrieval_tool,
    "serpapi_web_search_tool": serpapi_web_search_tool
}

async def call_mcp_tool(name, args):
    print(f"Executing tool: {name} with args: {args}")
    try:
        if name in TOOL_MAPPING:
            func = TOOL_MAPPING[name]
            # Simple dispatch
            if name == "machine_learning_faq_retrieval_tool":
                return func(query=args.get("query"))
            elif name == "serpapi_web_search_tool":
                return func(query=args.get("query"))
            else:
                return func(**args)
        else:
            return f"Tool {name} not found."
    except Exception as e:
        return f"Error executing tool: {e}"

async def main():
    chat = model.start_chat()
    print("Antigravity Client (Gemini + MCP) Started. Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            response = chat.send_message(user_input)
            
            # Simple loop to handle up to 3 chained tool calls
            for i in range(3):
                function_call_part = None
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_call_part = part
                        break
                
                if function_call_part:
                    fc = function_call_part.function_call
                    name = fc.name
                    args = dict(fc.args)
                    
                    tool_result = await call_mcp_tool(name, args)
                    print(f"Tool Result ({len(str(tool_result))} chars): {str(tool_result)[:100]}...")
                    
                    # Send result back to model
                    response = chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=name,
                                    response={"result": tool_result}
                                )
                            )]
                        )
                    )
                else:
                    # No more tool calls, print text and break loop
                    try:
                        print(f"AI: {response.text}")
                    except ValueError:
                        print("AI: [Model returned non-text response]")
                    break
            else:
                print("AI: [Stopped after 3 tool calls to prevent infinite loop]")
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
