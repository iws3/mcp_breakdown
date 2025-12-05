from server import run_analysis
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing analyze_stock_and_plot...")
result = run_analysis("Compare Google and Amazon stock performance over the last year")
print("\n--- Result ---")
print(result)

if os.path.exists("stock_plot.png"):
    print("\nSUCCESS: stock_plot.png exists.")
else:
    print("\nFAILURE: stock_plot.png does not exist.")
