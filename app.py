import streamlit as st
import pandas as pd
import yfinance as yf
import io
import requests

# 1. System Layout Configuration
st.set_page_config(page_title="Aegis Capital Flow Monitor Pro", layout="wide")

st.title("🛡️ Aegis Capital Flow Monitor Pro")
st.markdown("### *Institutional Money Flow, Insider Audit & AI Market Briefings*")
st.markdown("---")

# 2. Hardcoded Institutional Reference Databases
SECTOR_MAP = {
    "XLK": "Technology", "XLF": "Financials", "XLY": "Consumer Discretionary",
    "XLC": "Communications", "XLI": "Industrials", "XLP": "Consumer Staples",
    "XLE": "Energy", "XLV": "Healthcare", "XLU": "Utilities",
    "XLB": "Materials", "XLRE": "Real Estate"
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
    
    # Clean structured formatting for direct human scannability
    briefing = f"""
    🤖 **Aegis AI Strategy Directive:**
    * **Primary Inflow Target Zones:** Real-time metrics highlight capital entering **{acc_list}**. Institutional algorithms are executing accumulation blocks here. Prioritise stock setups inside these sectors.
    * **Risk Warning Zones:** Distribution pressures are currently expanding inside **{dist_list}**. Avoid chasing breakout narratives in these groups, as institutions are likely routing liquidity outward to park cash elsewhere.
    """
    return briefing

# 5. Cached Core Mathematics Core Pipeline Engine
@st.cache_data(ttl=3600)
def fetch_market_insights(_vol_sensitivity_param):
    try:
        bench = yf.Ticker("SPY").history(period="6m")
        if len(bench) < 30: return pd.DataFrame()
        bench['B_Ret'] = bench['Close'].pct_change(periods=20)
    except:
        return pd.DataFrame()
    
    sector_rows = []
    for etf, name in SECTOR_MAP.items():
        try:
            sec_df = yf.Ticker(etf).history(period="6m")
            if len(sec_df) < 30: continue
            
            sec_df['S_Ret'] = sec_df['Close'].pct_change(periods=20)
            recent_vol = sec_df['Volume'].iloc[-5:].mean()
            base_vol = sec_df['Volume'].mean()
            vol_mult = recent_vol / base_vol if base_vol > 0 else 0
            
            c_alpha = sec_df['S_Ret'].iloc[-1] - bench['B_Ret'].iloc[-1]
            p_alpha = sec_df['S_Ret'].iloc[-5] - bench['B_Ret'].iloc[-5]
            accel = c_alpha - p_alpha
            
            if vol_mult > _vol_sensitivity_param and accel > 0:
                status = "🚨 INFLOW ACCUMULATION"
            elif vol_mult > _vol_sensitivity_param and accel < 0:
                status = "⚠️ OUTFLOW DISTRIBUTION"
            else:
                status = "Neutral / Consolidation"
                
            sector_rows.append({
                "Sector": name, "ETF": etf, "Vol Multiplier": round(vol_mult, 2),
                "Alpha Accel": round(accel * 100, 2), "Status": status
            })
        except: continue
    return pd.DataFrame(sector_rows)

# 6. Main Core Application Engine Run Script Execution Loop
if st.button("🚀 Run Complete Aegis Market Scan"):
    with st.spinner("Analyzing institutional data and assembling AI brief..."):
        
        sector_df = fetch_market_insights(_vol_sensitivity_param=vol_sensitivity)
        
        if sector_df.empty:
            st.error("Market data feeds could not be loaded. Please re-run the scan engine.")
        else:
            # Separate active sectors for the AI logic engine
            acc_sec = sector_df[sector_df["Status"].str.contains("INFLOW")]["Sector"].tolist()
            dist_sec = sector_df[sector_df["Status"].str.contains("OUTFLOW")]["Sector"].tolist()
            
            # --- INTERACTIVE VISUAL INTEGRATION LAYER: THE AI BRIEFING BOX ---
            ai_box_content = generate_ai_briefing(acc_sec, dist_sec)
            st.info(ai_box_content)
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📁 Sector Capital Heatmap")
                def style_status(val):
                    if "INFLOW" in str(val): return 'background-color: #1e3d2f; color: #4ade80'
                    if "OUTFLOW" in str(val): return 'background-color: #4c1d1d; color: #f87171'
                    return ''
                st.dataframe(sector_df.style.applymap(style_status, subset=['Status']), use_container_width=True)
                
            with col2:
                st.subheader("🎯 Active Stock Deep-Dive")
                if not acc_sec:
                    st.info("No sectors displaying strong institutional inflows under current configurations.")
                else:
                    stock_rows = []
                    for sector_name in acc_sec:
                        for symbol in DEFAULT_WATCHLIST.get(sector_name, []):
                            try:
                                t = yf.Ticker(symbol)
                                info = t.info
                                rev_g = info.get('revenueGrowth', 0) if info.get('revenueGrowth') is not None else 0
                                margin = info.get('profitMargins', 0) if info.get('profitMargins') is not None else 0
                                
                                hist = t.history(period="1y")
                                current_price = hist['Close'].iloc[-1]
                                moving_avg = hist['Close'].rolling(window=200).mean().iloc[-1]
                                technical_pass = current_price > moving_avg
                                
                                insider = t.insider_transactions
                                insider_verdict = "Neutral"
                                if insider is not None and not insider.empty:
                                    insider.columns = [c.strip().lower() for c in insider.columns]
                                    buys = len(insider.head(10)[insider.head(10)['text'].str.contains('buy|purchase', case=False, na=False)])
                                    sales = len(insider.head(10)[insider.head(10)['text'].str.contains('sale|sell', case=False, na=False)])
                                    if buys > sales: insider_verdict = "🟢 Executives Buying"
                                    elif sales > buys: insider_verdict = "🔴 Executives Selling"
                                
                                if rev_g >= min_rev and margin >= min_margin and technical_pass:
                                    decision = "✅ HIGH CONVICTION BUY" if "Buying" in insider_verdict else "👀 Watch / Hold"
                                else:
                                    decision = "❌ Skip (Fails Rules)"
                                    
                                stock_rows.append({
                                    "Stock": symbol, "Sector": sector_name, "Rev Growth": f"{round(rev_g*100,1)}%",
                                    "Margin": f"{round(margin*100,1)}%", "Insiders": insider_verdict, "Final Verdict": decision
                                })
                            except: continue
                            
                    if stock_rows:
                        st.dataframe(pd.DataFrame(stock_rows), use_container_width=True)
                    else:
                        st.warning("No tracked tickers inside active sectors passed core logic checks.")