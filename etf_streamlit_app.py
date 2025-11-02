import streamlit as st
import yfinance as yf
import numpy as np

st.set_page_config(page_title="ETF Analyzer", layout="centered")

st.title("📊 ETF Analyzer")
st.write("Enter any US ETF symbol (e.g., SPY, QQQ, VTI, ARKK, INDA)")

symbol = st.text_input("ETF Symbol").upper().strip()

if symbol:
    try:
        etf = yf.Ticker(symbol)
        hist = etf.history(period="1y")

        if hist.empty:
            st.error("No data found. Check the symbol and try again.")
        else:
            hist["Daily Return"] = hist["Close"].pct_change()
            avg_return = hist["Daily Return"].mean() * 252
            volatility = hist["Daily Return"].std() * np.sqrt(252)
            sharpe_ratio = avg_return / volatility if volatility != 0 else 0

            current_price = hist["Close"][-1]
            high_52wk = hist["Close"].max()
            low_52wk = hist["Close"].min()
            strength_52wk = (current_price - low_52wk) / (high_52wk - low_52wk)

            info = etf.info
            pe_ratio = info.get("trailingPE", "N/A")
            dividend_yield = info.get("dividendYield", 0)
            if dividend_yield != "N/A" and dividend_yield:
                dividend_yield *= 100

            score = 0
            if sharpe_ratio > 1: score += 2
            elif sharpe_ratio > 0.5: score += 1
            if dividend_yield != "N/A" and dividend_yield > 1.5: score += 1
            if pe_ratio != "N/A" and pe_ratio < 25: score += 1
            if strength_52wk > 0.6: score += 1

            if score >= 4:
                verdict = "✅ BUY"
            elif score >= 2:
                verdict = "⚖️ HOLD"
            else:
                verdict = "❌ SELL"

            st.subheader(f"Results for {symbol}")
            st.metric("Current Price", f"${current_price:.2f}")
            st.metric("Average Annual Return", f"{avg_return:.2%}")
            st.metric("Volatility", f"{volatility:.2%}")
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
            st.metric("52W Strength", f"{strength_52wk:.1%}")
            st.write(f"**P/E Ratio:** {pe_ratio}")
            st.write(f"**Dividend Yield:** {dividend_yield}%")
            st.success(f"Final Verdict: {verdict}")
    except Exception as e:
        st.error(f"Error: {e}")
