from finance_crew import FinancialCrew
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not found in .env")
    exit(1)

print("Starting Financial Crew Test...")
crew = FinancialCrew()
try:
    result = crew.run("How has Microsoft (MSFT) performed over the last 6 months?")
    print("\n--- Result ---")
    print(result)
    print("\n--- Test Complete ---")
except Exception as e:
    print(f"\nError during execution: {e}")
