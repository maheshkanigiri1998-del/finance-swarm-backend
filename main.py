from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
from google import genai
import os
from dotenv import load_dotenv

# Initialize application and microservice configurations
load_dotenv()
app = FastAPI(
    title="Institutional Risk Swarm API",
    description="Asynchronous backend microservice delivering consolidated valuations and single-call adversarial investment debates."
)

# Enable Cross-Origin Resource Sharing (CORS) for global frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For secure production, map your exact Vercel web domain URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define robust input/output contract validation schemas using Pydantic
class TickerRequest(BaseModel):
    ticker: str

class AnalysisResponse(BaseModel):
    ticker: str
    currency: str
    currency_symbol: str
    current_price: float
    intrinsic_value: float | str
    margin_of_safety: float | str
    valuation_status: str
    market_cap: str
    pe_ratio: str
    eps_trailing: str
    ebitda_margin: str
    revenue_growth_yoy: str
    consensus: str
    bull_case: str
    bear_case: str

# ====================================================================================
# MICROSERVICE OPERATIONAL ENGINE CORE
# ====================================================================================
def execute_financial_pipeline(ticker_str: str) -> dict:
    """Processes financial statement boundaries, runs Graham calculations, and parses swarms."""
    clean_ticker = ticker_str.strip().upper()
    stock = yf.Ticker(clean_ticker)
    info = stock.info
    
    if not info or 'currentPrice' not in info:
        raise ValueError("Asset data unavailable or invalid ticker symbol.")
        
    # Sovereign Yield Anchors and Currency Baseline Mapping
    raw_currency = info.get('financialCurrency', 'USD')
    if clean_ticker.endswith(".NS"):
        currency_symbol, display_currency, risk_free_rate = "₹", "INR", 7.0
    elif clean_ticker.endswith(".L"):
        currency_symbol, display_currency, risk_free_rate = "£", "GBP", 4.2
    elif raw_currency == "INR":
        currency_symbol, display_currency, risk_free_rate = "₹", "INR", 7.0
    elif raw_currency == "GBP":
        currency_symbol, display_currency, risk_free_rate = "£", "GBP", 4.2
    else:
        currency_symbol, display_currency, risk_free_rate = "$", "USD", 4.4

    # Pence-to-Pounds Alignment Safety Check
    raw_price = info.get('currentPrice', 0.0)
    math_price = raw_price / 100 if (display_currency == "GBP" and raw_price > 1000) else raw_price

    # Mathematical Valuation Logic (Benjamin Graham Equation)
    eps = info.get('trailingEps')
    rev_growth = info.get('revenueGrowth')
    
    intrinsic_value = "N/A"
    margin_of_safety = "N/A"
    valuation_status = "Insufficient Fundamental Data"
    
    if isinstance(eps, (int, float)) and isinstance(rev_growth, (int, float)) and math_price > 0 and eps > 0:
        g = min(rev_growth * 100, 25.0)
        if g < 0: g = 0  
        intrinsic_value = float((eps * (8.5 + (2 * g)) * 4.4) / risk_free_rate)
        margin_of_safety = float(((intrinsic_value - math_price) / math_price) * 100)
        
        if margin_of_safety > 15:
            valuation_status = "UNDERVALUED"
        elif margin_of_safety < -15:
            valuation_status = "OVERVALUED"
        else:
            valuation_status = "FAIRLY VALUED"

    # Compile Structured Raw Data Indicators
    market_cap_val = info.get('marketCap')
    market_cap_str = f"{currency_symbol}{market_cap_val:,}" if market_cap_val else "N/A"
    
    # --- CONSOLIDATED SINGLE-CALL ADVERSARIAL SWARM CONTEXT ENGINE ---
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    context = f"Asset: {clean_ticker}. Price: {math_price}, Intrinsic Value: {intrinsic_value}, MoS: {margin_of_safety}%. P/E: {info.get('trailingPE')}, EBITDA Margins: {info.get('ebitdaMargins')}."
    
    unified_swarm_prompt = f"""
    {context}
    You are an elite Investment Committee AI Swarm composed of two competing voices.
    Analyze the financial asset details above and provide exactly two distinct research perspectives.
    
    [START_BULL]
    Provide a high-conviction institutional BULL CASE. Focus on structural moats and catalysts. Use 3 sharp bullet points.
    [END_BULL]
    
    [START_BEAR]
    Provide a defensive activist short-seller BEAR CASE. Focus on margin decays and tail risks. Use 3 sharp bullet points.
    [END_BEAR]
    """
    
    try:
        # Executes exactly one network query to maximize speed and prevent API server throttling
        response = client.models.generate_content(model='gemini-2.5-flash', contents=unified_swarm_prompt)
        full_text = response.text
        
        # Parse the separate cases using structural boundary tags
        if "[START_BULL]" in full_text and "[START_BEAR]" in full_text:
            bull_text = full_text.split("[START_BULL]")[1].split("[END_BULL]")[0].strip()
            bear_text = full_text.split("[START_BEAR]")[1].split("[END_BEAR]")[0].strip()
        else:
            bull_text = full_text
            bear_text = "Analysis compiled within primary layout payload matrix configuration."
            
    except Exception as api_err:
        bull_text = f"⚠️ **API Limit Notification:** Swarm collection throttled. Underlying details: {str(api_err)}"
        bear_text = "⚠️ **API Limit Notification:** Swarm connection throttled. Please execute pipeline request sequence again."

    return {
        "ticker": clean_ticker,
        "currency": display_currency,
        "currency_symbol": currency_symbol,
        "current_price": float(math_price),
        "intrinsic_value": intrinsic_value,
        "margin_of_safety": margin_of_safety,
        "valuation_status": valuation_status,
        "market_cap": market_cap_str,
        "pe_ratio": str(info.get('trailingPE', 'N/A')),
        "eps_trailing": str(info.get('trailingEps', 'N/A')),
        "ebitda_margin": f"{info.get('ebitdaMargins', 0.0) * 100:.2f}%" if info.get('ebitdaMargins') else 'N/A',
        "revenue_growth_yoy": f"{info.get('revenueGrowth', 0.0) * 100:.2f}%" if info.get('revenueGrowth') else 'N/A',
        "consensus": str(info.get('recommendationKey', 'N/A').upper().replace('_', ' ')),
        "bull_case": bull_text,
        "bear_case": bear_text
    }

# ====================================================================================
# ENDPOINT NETWORK ROUTING
# ====================================================================================
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_asset_endpoint(request: TickerRequest):
    """Secure POST endpoint executing corporate data compilation and synchronized debate loops."""
    try:
        payload = execute_financial_pipeline(request.ticker)
        return payload
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))