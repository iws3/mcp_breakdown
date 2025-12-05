from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from pydantic import BaseModel, Field
import os
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Define the LLM
# CrewAI supports Gemini via the 'gemini' provider string or LLM class
# We will use the LLM class for better control if needed, or just the string.
# Using 'gemini/gemini-1.5-flash' is the standard way in newer CrewAI versions.
my_llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# --- Tools ---

class StockAnalysisTools:
    # @tool("Get Stock History")
    def get_stock_history(ticker: str, period: str = "1y"):
        """
        Fetches historical stock data for a given ticker and period.
        Args:
            ticker: The stock ticker symbol (e.g., AAPL, TSLA).
            period: The period to fetch data for (e.g., 1mo, 3mo, 1y, 5y, max).
        Returns:
            A string summary of the dataframe head and description.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            return hist.to_string()
        except Exception as e:
            return f"Error fetching stock data: {e}"

# --- Agents ---

class FinancialCrew:
    def __init__(self):
        self.llm = my_llm

    def run(self, query: str):
        # 1. Query Parser Agent
        # Extracts structured intent from the user's natural language query.
        parser_agent = Agent(
            role='Senior Financial Data Analyst',
            goal='Accurately interpret user queries to extract stock tickers and analysis requirements.',
            backstory="""You are an expert at understanding financial requests. 
            You know exactly what data is needed to answer questions about stock trends, 
            comparisons, and performance.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # 2. Code Writer Agent
        # Writes Python code to analyze data and create plots.
        writer_agent = Agent(
            role='Python Financial Data Visualizer',
            goal='Write executable Python code to fetch data using yfinance and plot it using matplotlib.',
            backstory="""You are a Python expert specializing in financial data visualization.
            You write clean, error-free code. 
            IMPORTANT: You MUST write code that saves the plot to a file named 'stock_plot.png' in the current directory.
            Do not use plt.show(). Use plt.savefig('stock_plot.png').
            You should use the 'yfinance' library to get data.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # 3. Code Executor Agent (Simplified for this demo)
        # In a real scenario, we'd use a secure sandbox. Here, we trust the generated code for the demo.
        # We will actually skip a separate executor agent for simplicity and have the writer output the code,
        # which the MCP server will then execute. 
        # HOWEVER, to follow the "Crew" structure, let's have an agent that reviews the code.
        reviewer_agent = Agent(
            role='Senior Code Reviewer',
            goal='Review the Python code to ensure it is safe, correct, and saves the plot as requested.',
            backstory="""You are a senior software engineer. You check code for errors and security issues.
            You ensure the code uses yfinance and matplotlib correctly and saves the output to 'stock_plot.png'.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        # --- Tasks ---

        task1 = Task(
            description=f"""Analyze the following user query: '{query}'.
            Identify the stock ticker(s) and the timeframe mentioned.
            If no timeframe is mentioned, default to '1y'.
            Output a clear summary of what needs to be done.""",
            agent=parser_agent,
            expected_output="A summary of the stock ticker and timeframe to analyze."
        )

        task2 = Task(
            description="""Based on the analysis, write a complete Python script.
            The script must:
            1. Import yfinance, pandas, and matplotlib.pyplot.
            2. Download the stock data for the identified ticker and timeframe.
            3. Plot the 'Close' price.
            4. Set the title and labels correctly.
            5. Save the plot to 'stock_plot.png'.
            6. Print 'Plot saved to stock_plot.png' at the end.
            
            Return ONLY the Python code block (markdown formatted).""",
            agent=writer_agent,
            expected_output="A Python script in a markdown code block."
        )

        # Instantiate Crew
        crew = Crew(
            agents=[parser_agent, writer_agent],
            tasks=[task1, task2],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    # Test run
    crew = FinancialCrew()
    print(crew.run("How has Tesla performed over the last year?"))
