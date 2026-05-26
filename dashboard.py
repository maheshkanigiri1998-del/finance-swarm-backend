import streamlit as st
import yfinance as yf
from google import genai
import os
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

# ====================================================================================
# 1. QUANTITATIVE DATA & VALUATION PIPELINE ENGINE
# ====================================================================================
class DataEngine:
    """Handles data extraction, currency normalization, and mathematical valuation logic."""
    def __init__(self, ticker_str):
        self.ticker_input = ticker_str.strip().upper()
        self.stock = yf.Ticker(self.ticker_input)
        self.info = self.stock.info
        self.currency_symbol = "$"
        self.display_currency = "USD"
        self.risk_free_rate = 4.4
        self.math_price = 0.0
        
        self._set_geography_baselines()
        self._normalize_pricing_units()

    def _set_geography_baselines(self):
        """Programmatically configures currency symbols and bond yield discount baselines."""
        raw_currency = self.info.get('financialCurrency', 'USD')
        
        if self.ticker_input.endswith(".NS"):
            self.currency_symbol = "₹"
            self.display_currency = "INR"
            self.risk_free_rate = 7.0  
        elif self.ticker_input.endswith(".L"):
            self.currency_symbol = "£"
            self.display_currency = "GBP"
            self.risk_free_rate = 4.2  
        elif raw_currency == "INR":
            self.currency_symbol = "₹"
            self.display_currency = "INR"
            self.risk_free_rate = 7.0
        elif raw_currency == "GBP":
            self.currency_symbol = "£"
            self.display_currency = "GBP"
            self.risk_free_rate = 4.2
        else:
            self.currency_symbol = "$"
            self.display_currency = "USD"
            self.risk_free_rate = 4.4

    def _normalize_pricing_units(self):
        """Aligns UK Pence listings into whole Pounds for strict formula calculation safety."""
        current_price = self.info.get('currentPrice', 0.0)
        if self.display_currency == "GBP" and current_price > 1000:
            self.math_price = current_price / 100
        else:
            self.math_price = current_price

    def calculate_graham_intrinsic_value(self):
        """Executes defensive Graham Intrinsic Value formula and calculates Margin of Safety."""
        eps = self.info.get('trailingEps')
        rev_growth = self.info.get('revenueGrowth')
        
        if isinstance(eps, (int, float)) and isinstance(rev_growth, (int, float)) and self.math_price > 0 and eps > 0:
            g = min(rev_growth * 100, 25.0)
            if g < 0: g = 0  
            intrinsic_value = (eps * (8.5 + (2 * g)) * 4.4) / self.risk_free_rate
            margin_of_safety = ((intrinsic_value - self.math_price) / self.math_price) * 100
            return intrinsic_value, margin_of_safety
        return None, None

    def format_currency_value(self, val):
        """Utility method to safely prefix localized currency symbols to numeric metrics."""
        if isinstance(val, (int, float)):
            if self.display_currency == "GBP" and val > 1000:
                val = val / 100
            return f"{self.currency_symbol}{val:,.2f}"
        return "N/A"

    def compile_raw_metrics_dictionary(self):
        """Extracts and organizes clean raw values for tabular layout and report exporting."""
        info = self.info
        return {
            "Market Cap": info.get('marketCap', 'N/A'),
            "P/E Ratio": info.get('trailingPE', 'N/A'),
            "EPS (Trailing)": info.get('trailingEps', 'N/A'),
            "52-Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52-Week Low": info.get('fiftyTwoWeekLow', 'N/A'),
            "EBITDA Margin": f"{info.get('ebitdaMargins', 0.0) * 100:.2f}%" if info.get('ebitdaMargins') else 'N/A',
            "Revenue Growth (YoY)": f"{info.get('revenueGrowth', 0.0) * 100:.2f}%" if info.get('revenueGrowth') else 'N/A',
            "Wall Street Consensus": info.get('recommendationKey', 'N/A').upper().replace('_', ' '),
            "Target High Price": info.get('targetHighPrice', 'N/A')
        }

# ====================================================================================
# 2. ADVERSARIAL AGENTIC SWARM ORCHESTRATOR
# ====================================================================================
class AgentSwarm:
    """Manages secure prompt compilation and adversarial AI model execution loops."""
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def run_adversarial_debate(self, engine, intrinsic, mos):
        """Spins concurrent calls for opposing theses with automated server fault handling."""
        context = f"""
        Asset: {engine.ticker_input}
        Market Price: {engine.math_price}, Intrinsic Value: {intrinsic}, Margin of Safety: {mos}%.
        P/E: {engine.info.get('trailingPE')}, EBITDA Margin: {engine.info.get('ebitdaMargins')}, Growth: {engine.info.get('revenueGrowth')}.
        """
        
        bull_prompt = f"{context}\nYou are an Institutional Permabull Analyst. Generate a high-conviction BULL CASE. Focus on structural moats, growth catalysts, and long-term upside. Provide 3 sharp bullet points."
        bear_prompt = f"{context}\nYou are an activist Short-Seller Bear Analyst. Generate a critical, defensive BEAR CASE. Focus on margin decay, competitive risks, and capital constraints. Provide 3 sharp bullet points."
        
        try:
            bull_response = self.client.models.generate_content(model='gemini-2.5-flash', contents=bull_prompt)
            bear_response = self.client.models.generate_content(model='gemini-2.5-flash', contents=bear_prompt)
            return bull_response.text, bear_response.text
        except Exception:
            fallback_bull = "⚠️ **Operational Interruption:** The Bull Agent is currently disconnected due to high API traffic volume."
            fallback_bear = "⚠️ **Operational Interruption:** The Bear Agent is currently disconnected due to high API traffic volume."
            return fallback_bull, fallback_bear

# ====================================================================================
# 3. REPORT EXPORT PROCESSING ENGINE (NEW STRUCTURAL MODULE)
# ====================================================================================
class ReportExporter:
    """Converts localized dataframes and AI case summaries into standalone binary Excel files."""
    @staticmethod
    def generate_excel_bytes(engine, metrics_dict, intrinsic, mos, bull_text, bear_text):
        """Compiles clean, separate tabs for quantitative and qualitative data layers inside Excel."""
        # 1. Structural Sheet A: Quantitative Core Metrics
        quant_data = {
            "Metric Indicator": list(metrics_dict.keys()) + ["Calculated Intrinsic Value", "Margin of Safety (%)"],
            "Value": list(metrics_dict.values()) + [intrinsic, f"{mos:.2f}%" if isinstance(mos, float) else "N/A"]
        }
        df_quant = pd.DataFrame(quant_data)

        # 2. Structural Sheet B: Qualitative Intelligence
        qual_data = {
            "Research Node Perspective": ["Institutional Bull Case Thesis", "Activist Short-Seller Bear Thesis"],
            "AI Agent Commentary Raw Text": [bull_text, bear_text]
        }
        df_qual = pd.DataFrame(qual_data)

        # 3. Build virtual in-memory spreadsheet stream
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_quant.to_excel(writer, sheet_name='Quantitative Valuation', index=False)
            df_qual.to_excel(writer, sheet_name='AI Intelligence Debate', index=False)
        
        processed_data = output.getvalue()
        return processed_data

# ====================================================================================
# 4. STREAMLIT INTERFACE MANAGER
# ====================================================================================
class RiskDashboard:
    """Manages UI/UX structures, table compilation, and interactive screen states."""
    @staticmethod
    def initialize():
        st.set_page_config(page_title="Agentic AI Risk Terminal", layout="wide")
        st.title("🛡️ Institutional Agentic Research Swarm")
        st.caption("Production-Grade Adversarial AI Analysts & Quantitative Valuation Engines")

    @staticmethod
    def render_metrics_table(engine, metrics_dict):
        st.subheader(f"📈 Strategic Fundamental Indicators ({engine.display_currency})")
        
        display_data = {
            "Financial Metric Indicator": list(metrics_dict.keys()),
            "Live Dashboard Value": [
                f"{engine.currency_symbol}{val:,}" if "Cap" in k and isinstance(val, (int, float)) else
                engine.format_currency_value(val) if "Price" in k or "High" in k or "Low" in k else str(val)
                for k, val in metrics_dict.items()
            ]
        }
        st.table(display_data)

# ====================================================================================
# 5. RUNTIME MAIN INTERACTION BLOCK
# ====================================================================================
if __name__ == "__main__":
    RiskDashboard.initialize()
    load_dotenv()
    
    st.sidebar.header("Swarm Control Parameters")
    ticker_input = st.sidebar.text_input("Enter Global Asset Ticker:", value="TSLA")
    execute = st.sidebar.button("Execute Agentic Swarm Pipeline")
    
    if execute and ticker_input:
        with st.spinner("Processing pipeline sequences..."):
            try:
                engine = DataEngine(ticker_input)
                intrinsic, mos = engine.calculate_graham_intrinsic_value()
                
                if mos is not None:
                    if mos > 15:
                        st.success(f"⚖️ **QUANT ENGINE JUDGEMENT: UNDERVALUED (Margin of Safety: +{mos:.2f}%)**")
                    elif mos < -15:
                        st.error(f"⚠️ **QUANT ENGINE JUDGEMENT: OVERVALUED (Premium Downside Risk: {mos:.2f}%)**")
                    else:
                        st.warning(f"⚖️ **QUANT ENGINE JUDGEMENT: FAIRLY VALUED (Deviation: {mos:.2f}%)**")
                
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Market Price", engine.format_currency_value(engine.info.get('currentPrice')))
                with c2: st.metric("Intrinsic Fair Value", f"{engine.currency_symbol}{intrinsic:,.2f}" if intrinsic else "N/A")
                with c3: st.metric("Valuation Margin of Safety", f"{mos:.2f}%" if mos else "N/A")
                
                # Fetch dictionary and render metrics table
                raw_metrics = engine.compile_raw_metrics_dictionary()
                RiskDashboard.render_metrics_table(engine, raw_metrics)
                
                st.subheader("🤖 Agentic AI Investment Swarm: Adversarial Debate")
                swarm = AgentSwarm(api_key=os.getenv("GOOGLE_API_KEY"))
                bull_text, bear_text = swarm.run_adversarial_debate(engine, intrinsic, mos)
                
                colBull, colBear = st.columns(2)
                with colBull:
                    st.success("### 💚 INSTITUTIONAL BULL CASE")
                    st.markdown(bull_text)
                with colBear:
                    st.error("### 🔴 STRUCTURAL BEAR CASE")
                    st.markdown(bear_text)
                
                # --- EXCEL REPORT EXPORT ACTION BLOCK ---
                st.subheader("📥 Export Institutional Risk Memo")
                st.markdown("Compile and download this entire session's quantitative models and qualitative arguments as a dual-tab spreadsheet.")
                
                # Call report generator class
                excel_file_bytes = ReportExporter.generate_excel_bytes(
                    engine, raw_metrics, intrinsic, mos, bull_text, bear_text
                )
                
                # Native Streamlit data stream download mechanism
                st.download_button(
                    label="📥 Download Comprehensive Financial Report (.xlsx)",
                    data=excel_file_bytes,
                    file_name=f"{engine.ticker_input}_Risk_Analysis_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                    
            except Exception as e:
                st.error(f"Pipeline Interruption: {str(e)}")
    else:
        st.info("👈 Enter a target asset ticker in the control panel and activate the operational architecture pipeline.")