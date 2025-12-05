import streamlit as st
import os
import sys
from dotenv import load_dotenv
from server import run_analysis, generate_story
import urllib.parse

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Financial Analyst Agent", 
    page_icon="📈",
    layout="wide"
)

# Custom CSS for a nicer look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #4CAF50;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .story-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
    }
    .highlight {
        color: #4CAF50;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Educational Story ---
with st.sidebar:
    st.image("C:/Users/THE EYE INFORMATIQUE/.gemini/antigravity/brain/67061ab2-6e0a-4a67-942e-d53d178a46a7/african_village_market_stock_concept_1764934999648.png", caption="The Village Market & The Stock Market")
    
    st.markdown("## 🌍 What is a Stock? (Explained Simply)")
    
    with st.expander("1. The Village Farm Story", expanded=True):
        st.markdown("""
        Imagine a man in your village who owns **a big farm**.
        He wants to grow — buy more land, hire workers. But he **doesn’t have enough money**.
        
        So he divides his farm into tiny pieces called **shares**.
        When **you buy one piece**, you become a tiny owner of the farm.
        
        ### 👉 **That’s what a stock is.**
        A **stock = a small piece of ownership in a company.**
        """)

    with st.expander("2. The Market"):
        st.markdown("""
        Imagine thousands of farms and businesses gathering in one big place like **Onitsha Market** or **Lagos Balogun Market**.
        
        But instead of yams or clothes, people buy and sell **stocks**.
        That big marketplace is the **Stock Market**.
        """)

    with st.expander("3. Why it Matters for Africa"):
        st.markdown("""
        Every rich country became rich because ordinary people invested in companies.
        Imagine if African youth consistently invested in:
        * MTN, Dangote, Safaricom
        * Global giants like Apple, Google
        
        We could build wealth **without leaving the continent**.
        """)

# --- Main Content ---

st.markdown('<p class="main-header">📈 MCP Financial Analyst Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your AI-Powered Financial Teacher & Advisor</p>', unsafe_allow_html=True)

st.markdown("""
<div class="story-box">
    <b>Welcome!</b> I am an AI agent designed to make financial analysis simple and accessible.
    I can fetch real-time data, analyze trends, and visualize stock performance for you.
    <br><br>
    Try asking me: <i>"Compare MTN and Airtel stock performance"</i> or <i>"How is Tesla doing this year?"</i>
</div>
""", unsafe_allow_html=True)

# Check API Key
if not os.getenv("GOOGLE_API_KEY"):
    st.error("⚠️ GOOGLE_API_KEY not found in .env file. Please set it to use the agent.")
    st.stop()

# User Input
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Enter your financial query:", placeholder="e.g., Compare Google and Amazon stock performance over the last year")
with col2:
    analyze_btn = st.button("Analyze 🚀", use_container_width=True)

if analyze_btn:
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("🤖 Agents are working... (Parsing -> Coding -> Plotting)"):
            try:
                # Call the function directly from server.py
                result = run_analysis(query)
                
                # Store in session state
                st.session_state['analysis_complete'] = True
                st.session_state['analysis_result'] = result
                st.session_state['current_query'] = query
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Display Results if analysis is complete
if st.session_state.get('analysis_complete'):
    # Create Tabs
    tab1, tab2 = st.tabs(["📊 Market Analysis", "🌍 Village Story"])
    
    with tab1:
        result = st.session_state['analysis_result']
        
        # Display Result
        st.success("Analysis Complete!")
        
        # Split result to separate message and code if possible
        if "Generated Code:" in result:
            message_part, code_part = result.split("Generated Code:", 1)
            st.markdown(message_part)
            with st.expander("View Generated Python Code"):
                st.code(code_part.replace("```python", "").replace("```", ""), language="python")
        else:
            st.markdown(result)
        
        # Check for and display the plot
        if os.path.exists("stock_plot.png"):
            st.image("stock_plot.png", caption="Generated Stock Analysis Plot", use_container_width=True)
        else:
            st.warning("No plot image found (stock_plot.png).")

    with tab2:
        st.info("Click the button below to hear the story behind the numbers.")
        
        # Use a unique key for this button to avoid conflicts
        if st.button("📖 Tell me the Story", key="story_btn"):
            with st.spinner("✨ Weaving a story..."):
                story, image_prompt = generate_story(st.session_state['current_query'])
                
                # Generate Image URL using Pollinations AI
                encoded_prompt = urllib.parse.quote(image_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true"
                
                st.markdown(f"### 🌿 The Story of {st.session_state['current_query']}")
                
                # Display Image
                st.image(image_url, caption=image_prompt, use_container_width=True)
                
                # Display Story
                st.markdown(f"""
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 5px solid #FFC107; font-size: 1.1em;">
                    {story}
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Powered by CrewAI, Gemini 2.5 Flash, FastMCP, and Pollinations AI.")
