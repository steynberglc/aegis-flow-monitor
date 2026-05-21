import streamlit as st
import pandas as pd
import yfinance as yf

# 1. System Layout Configuration
st.set_page_config(page_title="Aegis Capital Flow Monitor Pro", layout="wide")
st.title("🛡️ Aegis Capital Flow Monitor Pro")
st.markdown("### *Institutional Money Flow, Insider Audit & AI Market Briefings*")
st.markdown("---")

# 2. Hardcoded Institutional Reference Databases
SECTOR_MAP = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLY": "Consumer Discretionary",
    "XLC": "Communications",
    "XLI": "Industrials",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLRE": "Real Estate"
}

DEFAULT_WATCHLIST = {
    "Technology": ["AAPL", "MSFT", "NVDA"],
    "Financials": ["JPM", "BAC", "GS"],
    "Energy": ["XOM", "CVX"],
    "Healthcare": ["JNJ", "LLY", "UNH"]
}

# 3. Sidebar Control Panels
st.sidebar.header("🎛️ System Control Panel")
sidebar_tab1, sidebar_tab2, sidebar_tab3 = st.sidebar.tabs(["⚙️ Settings", "📖 Glossary", "🧩 Guide"])

with sidebar_tab1:
    st.subheader("Fundamental Limits")
    min_rev = st.slider("Minimum Revenue Growth", 0.0, 0.30, 0.05, step=0.01)
    min_margin = st.slider("Minimum Profit Margin", 0.0, 0.50, 0.10, step=0.01)
    st.markdown("---")
    vol_sensitivity = st.slider("Institutional Vol Multiplier", 1.0, 2.0, 1.15, step=0.05)

with sidebar_tab2:
    st.subheader("System Glossary")
    st.markdown("- **Inflow**: Funds are buying positions.\n- **Distribution**: Funds are unloading shares onto retail.")

with sidebar_tab3:
    st.subheader("Operational Steps")
    st.markdown("1. Set thresholds.\n2. Click Run Complete Market Scan.")

# 4. Local AI Summary Generation Function
def generate_ai_briefing(accumulating_sectors, distributing_sectors):
    """Generates an immediate structural market context briefing based on findings."""
    acc_list = ", ".join(accumulating_sectors) if accumulating_sectors else "None"
    dist_list = ", ".join(distributing_sectors) if distributing_sectors else "None"
    
    briefing = f"""
    🤖 **Aegis AI Strategy Directive:**
    * **Primary Inflow Target Zones:** Real-time metrics highlight capital entering **{acc_list}**. Institutional algorithms are executing accumulation blocks here. Prioritise stock setups inside these sectors.
    * **Risk Warning Zones:** Distribution pressures are currently expanding inside **{dist_list}**. Avoid chasing breakout narratives in these groups, as institutions are likely routing liquidity outward to park cash elsewhere.
    """
    return briefing

# 5. Cached Core Mathematics Pipeline Engine
@st.cache_data(ttl=3600)
def fetch_market_insights(_vol_sensitivity_param):
    try:
        # Fetch SPY benchmark using explicitly flattened index properties
        bench = yf.download("SPY", period="6m", progress=False, auto_adjust=True, multi_level_index=False)
        if bench.empty or len(bench) < 30:
            return pd.DataFrame()
        
        # Standardize MultiIndex structures into simple clean columns if forced by the API
        if isinstance(bench.columns, pd.MultiIndex):
            bench.columns = [col[0] if isinstance(col, tuple) else col for col in bench.columns]
            
        bench['B_Ret'] = bench['Close'].pct_change(periods=20)
    except Exception as e:
        st.sidebar.error(f"Engine Warning: {str(e)}")
        return pd.DataFrame()
        
    sector_rows = []
    for etf, name in SECTOR_MAP.items():
        try:
            # Download specific target sector data matrix
            sec_df = yf.download(etf, period="6m", progress=False, auto_adjust=True, multi_level_index=False)
            if sec_df.empty or len(sec_df) < 30:
                continue
                
            if isinstance(sec_df.columns, pd.MultiIndex):
                sec_df.columns = [col[0] if isinstance(col, tuple) else col for col in sec_df.columns]
                
            sec_df['S_Ret'] = sec_df['Close'].pct_change(periods=20)
            
            # Mathematics processing via structural float isolates
            recent_vol = float(sec_df['Volume'].iloc[-5:].mean())
            base_vol = float(sec_df['Volume'].mean())
            vol_mult = recent_vol / base_vol if base_vol > 0 else 0
            
            c_alpha = float(sec_df['S_Ret'].iloc[-1] - bench['B_Ret'].iloc[-1])
            p_alpha = float(sec_df['S_Ret'].iloc[-5] - bench['B_Ret'].iloc[-5])
            accel = c_alpha - p_alpha
            
            # Status resolution architecture logic
            if vol_mult > _vol_sensitivity_param and accel > 0:
                status = "Institutional Inflow"
            elif vol_mult > _vol_sensitivity_param and accel <= 0:
                status = "Distribution"
            else:
                status = "Neutral Turnover"
                
            sector_rows.append({
                "Sector": name,
                "Ticker": etf,
                "Volume Multiplier": round(vol_mult, 2),
                "Alpha Acceleration": round(accel, 4),
                "Status": status
            })
        except:
            continue
            
    return pd.DataFrame(sector_rows)

# 6. Execution and Interface Layout Execution
if st.button("Run Complete Market Scan", type="primary"):
    with st.spinner("Analyzing institutional pipelines..."):
        df_insights = fetch_market_insights(vol_sensitivity)
        
        if not df_insights.empty:
            # Isolate categories for the local AI summary generation pipeline
            acc_sectors = df_insights[df_insights["Status"] == "Institutional Inflow"]["Sector"].tolist()
            dist_sectors = df_insights[df_insights["Status"] == "Distribution"]["Sector"].tolist()
            
            # Render structured briefing box
            st.info(generate_ai_briefing(acc_sectors, dist_sectors))
            
            # Render quant core summary database frame
            st.subheader("📊 Quant Flow Matrix Summary")
            st.dataframe(df_insights, use_container_width=True, hide_index=True)
        else:
            st.error("Market feeds cannot be loaded. Please ensure you have run 'pip install --upgrade yfinance' in your console.")