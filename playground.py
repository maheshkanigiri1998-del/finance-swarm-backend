import phi
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.yfinance import YFinanceTools
from phi.playground import Playground, serve_playground_app
from dotenv import load_dotenv

# 1. Load Gemini API key from .env
load_dotenv()

# 2. Build the Web Analyst
web_analyst = Agent(
    name="Web Analyst",
    role="Scout current market sentiment, corporate news headlines, and recent industry trends.",
    model=Gemini(id="gemini-2.5-flash"),
    instructions=[
        "Use your internal search capability to find recent market news from the last 3-6 months.",
        "Summarize the key trends and provide context on the industry."
    ],
    markdown=True,
)

# 3. Build the Core Financial Modeler
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
    markdown=True,
)

# 4. Deploy the agents into a Browser Playground Interface
app = Playground(agents=[web_analyst, finance_modeler]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)