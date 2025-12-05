from rag_app import Retriver, QdrantVDB, EmbededData
import os
import sys
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()

# Initialize MCP Server
mcp = FastMCP("MCP AGENTIC RAG SERVER")

# Initialize RAG components globally to avoid reloading model on every request
try:
    print("Initializing RAG components...", file=sys.stderr)
    # These will be initialized when the module is imported
    embedder = EmbededData()
    vdb = QdrantVDB("ml_faq_collection")
    retriever = Retriver(vdb, embedder)
    print("RAG components initialized.", file=sys.stderr)
except Exception as e:
    print(f"Warning: Failed to initialize RAG components: {e}", file=sys.stderr)
    retriever = None

@mcp.tool()
def machine_learning_faq_retrieval_tool(query:str)->str:
    """
    Retrieves the most relevant documents from the machine learning FAQ collection, Use this  tool when the user ask about ML
    
    input:
        query:str->the user query to retrieve the most relevant documents from the machine learning FAQ collection.
        
    output:
        response:str -> most relevant documents retrieved from the vector DB
    """
    # check type of text
    if not isinstance(query, str):
        raise ValueError("Query must be a string.")
    
    if retriever is None:
        return "Error: RAG system is not initialized. Please check server logs."
    
    return retriever.search(query)


@mcp.tool()
def serpapi_web_search_tool(query:str)->list[str]:
    """
    Search for information on a given topic using SerpAPI (Google Search).
    
    input:
        query:str->the user query to search for information
    output:
        context:list[str]->list of most relevant web search results
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return ["Error: SERPAPI_API_KEY not set in environment."]

    try:
        search = GoogleSearch({
            "q": query,
            "api_key": api_key,
            "num": 5
        })
        results = search.get_dict()
        
        if "error" in results:
            return [f"SerpAPI Error: {results['error']}"]
            
        organic_results = results.get("organic_results", [])
        
        if not organic_results:
             return ["No results found. This might be due to an API issue or no matches."]
        
        # Format results for better consumption
        formatted_results = []
        for result in organic_results:
            title = result.get("title", "No Title")
            link = result.get("link", "#")
            snippet = result.get("snippet", "No Snippet")
            formatted_results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")
            
        return formatted_results
    except Exception as e:
        return [f"Error performing search: {str(e)}"]

# starting the RAG MCP SERVER
if __name__=="__main__":
    # Use stdio transport for Claude Desktop compatibility
    print("Starting MCP Server on stdio...", file=sys.stderr)
    mcp.run()