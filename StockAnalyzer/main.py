import streamlit as st
from analysis import analyze_stock
from llm_report import generate_swot_report, save_swot_pdf
from voiceover import generate_voiceover
from matplotlib import pyplot as plt

st.set_page_config(page_title="📊 Stock Analyzer & Reporter", layout="wide")

# -------------------------------
# UI Header
# -------------------------------
st.markdown("""
<style>
.title {
    font-size: 36px;
    font-weight: bold;
    color: #f8a900;
}
.subtitle {
    font-size: 20px;
    color: #999;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>📈 Stock Market Analyzer & Reporter</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Analyze Indian stocks with technical indicators, LLM-based SWOT, and voice reports</div>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# Input
# -------------------------------

stock_options = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Wipro": "WIPRO.NS",
    "Hindustan Unilever": "HINDUNILVR.NS"
}

selected_company = st.selectbox("📌 Select a Company", options=list(stock_options.keys()))
ticker = stock_options[selected_company]

period = st.radio("📅 Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], horizontal=True)

# -------------------------------
# Analyze Button
# -------------------------------
if st.button("🚀 Run Full Analysis"):
    with st.spinner("⏳ Fetching data and running analysis..."):
        hist, info, sentiment = analyze_stock(ticker, period)
        swot = generate_swot_report(info, sentiment)
        pdf_file = save_swot_pdf(swot)
        audio_file = generate_voiceover(swot)

    # -------------------------------------
    # TABS Layout
    # -------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Price & Indicators", "📰 Sentiment", "🧠 SWOT + PDF", "🔊 Voice Report"])

    #tab1-price chart
    with tab1:
        st.subheader("📈 Stock Price + Indicators")
        fig, ax = plt.subplots(3, figsize=(12, 9))
        ax[0].plot(hist['Close'], label="Close", color='blue')
        ax[0].plot(hist['MA20'], label="MA20", color='orange')
        ax[0].plot(hist['MA50'], label="MA50", color='green')
        ax[0].legend()
        ax[0].set_title("Price + Moving Averages")

        ax[1].bar(hist.index, hist['Volume'], label="Volume", color='purple')
        ax[1].legend()
        ax[1].set_title("Volume")

        ax[2].plot(hist['RSI'], label="RSI", color='red')
        ax[2].axhline(70, color='black', linestyle='--')
        ax[2].axhline(30, color='black', linestyle='--')
        ax[2].legend()
        st.pyplot(fig)

    #tab2-sentiment
    with tab2:
        st.subheader("📰 Real-Time News Sentiment (Powered by Gemini Flash 🔥)")
        st.markdown(f"**{selected_company}** sentiment analysis based on live news:")
        st.markdown(sentiment)

    #tab3-swot
    with tab3:
        st.subheader("🧠 AI SWOT Analysis (EURI GPT-4.1 Nano)")
        st.code(swot, language='markdown')
        st.download_button("📥 Download SWOT PDF", data=open(pdf_file, "rb"), file_name=pdf_file)

    #tab4-voice
    with tab4:
        st.subheader("🔊 Voice Report (Text-to-Speech)")
        st.audio(audio_file)
else:
    st.markdown("👈 Choose a stock and run the analysis to see results.")