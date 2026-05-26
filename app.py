from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

# 1. Load your Gemini API key from the .env file
load_dotenv()

# 2. Build the Market Researcher Agent using Gemini's native Google Search Grounding
web_analyst = Agent(
    name="Web Analyst",
    role="Scout current market sentiment, corporate news headlines, and recent industry trends.",
    model=Gemini(id="gemini-2.5-flash"),
    # Enforces native Google Search instead of third-party scraping libraries
    tools=[], 
    instructions=[
        "Use your internal search capability to find recent market news from the last 3-6 months.",
        "Summarize the key trends and provide context on the industry."
    ],
    show_tool_calls=True,
    markdown=True,
)

# 3. Build the Core Financial Modeler Agent (This part works great!)
finance_modeler = Agent(
    name="Financial Modeler",
    role="Extract financial statements and analyze company metrics from Yahoo Finance.",
    model=Gemini(id="gemini-2.5-flash"),
    tools=[YFinanceTools(
        stock_price=True, 
        analyst_recommendations=True, 
        company_info=True, 
        historical_prices=True
    )],
    instructions=["Format all financial figures cleanly.", "Present metrics in clear Markdown tables."],
    show_tool_calls=True,
    markdown=True,
)

# 4. Build the Orchestrator to compile the clean report
financial_swarm = Agent(
    name="Financial Swarm Orchestrator",
    model=Gemini(id="gemini-2.5-flash"), 
    team=[web_analyst, finance_modeler],
    instructions=[
        "Synthesize the financial data from the Financial Modeler and market trends from the Web Analyst.",
        "Compare fundamental metrics (like P/E and growth) against current qualitative news.",
        "Conclude with a clear summary evaluating whether the growth looks sustainable."
    ],
    show_tool_calls=True,
    markdown=True,
)

# 5. Execute the query
if __name__ == "__main__":
    financial_swarm.print_response(
        "Analyze stock symbol SUZLON.NS. Give me their key financial metrics, recent news, and tell me if the growth looks sustainable.", 
        stream=True
    )