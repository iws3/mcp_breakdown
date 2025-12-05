from fastmcp import FastMCP
from finance_crew import FinancialCrew
import os
import sys
import re
import subprocess

# Initialize MCP Server
mcp = FastMCP("MCP FINANCIAL ANALYST")

import google.generativeai as genai
import urllib.parse

# Configure Gemini directly for the story generation
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_story(query: str) -> tuple[str, str]:
    """
    Generates a simple story explanation and an image prompt.
    Returns: (story_text, image_prompt)
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a wise African storyteller.
    Explain the financial concept or stock trend related to: "{query}"
    
    Target Audience: A 12-year-old African child.
    Analogy: Use a village market, farming, or trading analogy (e.g., yams, cattle, rain).
    Tone: Inspiring, educational, simple, and warm.
    Length: Under 150 words.
    
    Also, provide a short, vivid image prompt that represents this story visually.
    
    Output Format:
    STORY: [The story text]
    IMAGE_PROMPT: [The image prompt]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse output
        story = ""
        image_prompt = ""
        
        if "STORY:" in text:
            parts = text.split("IMAGE_PROMPT:")
            story = parts[0].replace("STORY:", "").strip()
            if len(parts) > 1:
                image_prompt = parts[1].strip()
        else:
            story = text
            image_prompt = f"African village market learning finance {query}"
            
        return story, image_prompt
    except Exception as e:
        return f"Could not generate story: {e}", ""

def run_analysis(query: str) -> str:
    """
    Core logic to analyze stock and plot.
    """
    try:
        print(f"Received query: {query}", file=sys.stderr)
        
        # 1. Run the Crew to get the Python code
        crew = FinancialCrew()
        result = crew.run(query)
        
        # CrewAI returns a CrewOutput object, we need the string
        result_str = str(result)
        
        print("Crew execution finished. Extracting code...", file=sys.stderr)
        
        # 2. Extract Python code from the result
        # Look for markdown code blocks
        code_match = re.search(r"```python(.*?)```", result_str, re.DOTALL)
        if not code_match:
            # Try looking for just ``` if python isn't specified
            code_match = re.search(r"```(.*?)```", result_str, re.DOTALL)
            
        if code_match:
            code = code_match.group(1).strip()
        else:
            # If no code block, assume the whole output might be code (risky, but fallback)
            # or return error
            return f"Error: Could not extract Python code from agent output:\n{result_str}"

        # 3. Save the code to a file
        script_path = "generated_stock_analysis.py"
        with open(script_path, "w") as f:
            f.write(code)
            
        print(f"Code saved to {script_path}. Executing...", file=sys.stderr)
        
        # 4. Execute the code
        # Security Warning: This executes generated code directly. 
        # In a production environment, this MUST be sandboxed (Docker, etc.).
        try:
            # Run the script using the current python interpreter
            subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
            
            # Check if plot exists
            if os.path.exists("stock_plot.png"):
                return f"Success! Analysis complete. The plot has been saved to 'stock_plot.png' in the server directory.\n\nGenerated Code:\n```python\n{code}\n```"
            else:
                return "The code executed successfully but 'stock_plot.png' was not found. Please check the generated code."
                
        except subprocess.CalledProcessError as e:
            return f"Error executing generated code:\n{e.stderr}\n\nCode:\n{code}"

    except Exception as e:
        return f"An error occurred during analysis: {str(e)}"

@mcp.tool()
def analyze_stock_and_plot(query: str) -> str:
    """
    Analyzes a stock based on a natural language query, generates Python code to visualize it,
    executes the code, and saves the plot.
    
    Args:
        query: The user's question, e.g., "Show me Apple's stock trend for the last 6 months."
        
    Returns:
        A status message indicating success or failure, and the path to the generated plot.
    """
    return run_analysis(query)

if __name__ == "__main__":
    print("Starting Financial Analyst MCP Server...", file=sys.stderr)
    mcp.run()
