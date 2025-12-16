import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import timedelta

from storage.db import MarketDataDB
from storage.resampler import resample_ticks
from analytics.spread_ols import compute_hedge_ratio, compute_spread
from analytics.zscore import compute_zscore
from analytics.rolling_corr import compute_rolling_corr
from alerts.alert_engine import check_zscore_alert

# ----------------------------------
# Initialization
# ----------------------------------
db = MarketDataDB()

if "alert_history" not in st.session_state:
    st.session_state.alert_history = []

# ----------------------------------
# Dashboard
# ----------------------------------
def run_dashboard():
    st.set_page_config(
        page_title="Real-Time Quant Analytics",
        layout="wide"
    )

    st.title("📊 Real-Time Quant Analytics Dashboard")

    export_df = None  # IMPORTANT: avoid UnboundLocalError

    # ----------------------------------
    # Sidebar Controls
    # ----------------------------------
    st.sidebar.header("Controls")

    symbols = st.sidebar.multiselect(
        "Select Symbols (Pairs)",
        ["BTCUSDT", "ETHUSDT"],
        default=["BTCUSDT", "ETHUSDT"]
    )

    timeframe = st.sidebar.selectbox(
        "Resample Timeframe",
        ["1s", "1min"]
    )

    window = st.sidebar.slider(
        "Rolling Window",
        min_value=10,
        max_value=120,
        value=30
    )

    lookback_minutes = st.sidebar.slider(
        "Lookback Period (minutes)",
        min_value=5,
        max_value=120,
        value=30
    )

    alert_threshold = st.sidebar.slider(
        "Z-Score Alert Threshold",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5
    )

    if len(symbols) != 2:
        st.warning("Please select exactly 2 symbols for pair analytics.")
        return

    # ----------------------------------
    # Data Fetching
    # ----------------------------------
    df = db.fetch_ticks(symbols, lookback_minutes=lookback_minutes)

    if df.empty:
        st.info("⏳ Waiting for market data...")
        return

    bars = resample_ticks(df, timeframe)

    if symbols[0] not in bars or symbols[1] not in bars:
        st.info("⏳ Insufficient data for selected timeframe.")
        return

    series_a = bars[symbols[0]]["close"]
    series_b = bars[symbols[1]]["close"]

    # ----------------------------------
    # Analytics
    # ----------------------------------
    beta = compute_hedge_ratio(series_a, series_b)
    spread = compute_spread(series_a, series_b, beta)
    zscore = compute_zscore(spread, window)
    corr = compute_rolling_corr(series_a, series_b, window)

    # ----------------------------------
    # Alerts
    # ----------------------------------
    alert_msg = check_zscore_alert(zscore, alert_threshold)
    if alert_msg:
        st.error(alert_msg)
        st.session_state.alert_history.append({
            "timestamp": zscore.index[-1],
            "message": alert_msg
        })

    if zscore.dropna().empty:
        st.info("⏳ Analytics warming up (collecting enough data)...")

    # ----------------------------------
    # Charts
    # ----------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price Chart")
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=series_a.index, y=series_a,
            name=symbols[0]
        ))
        fig_price.add_trace(go.Scatter(
            x=series_b.index, y=series_b,
            name=symbols[1]
        ))
        fig_price.update_layout(height=350)
        st.plotly_chart(fig_price, use_container_width=True)

    with col2:
        st.subheader("Spread")
        fig_spread = go.Figure()
        fig_spread.add_trace(go.Scatter(
            x=spread.index, y=spread,
            name="Spread"
        ))
        fig_spread.update_layout(height=350)
        st.plotly_chart(fig_spread, use_container_width=True)

    st.subheader("Z-Score")
    fig_z = go.Figure()
    fig_z.add_trace(go.Scatter(
        x=zscore.index, y=zscore,
        name="Z-Score"
    ))
    fig_z.add_hline(y=alert_threshold, line_dash="dash", line_color="red")
    fig_z.add_hline(y=-alert_threshold, line_dash="dash", line_color="green")
    fig_z.update_layout(height=300)
    st.plotly_chart(fig_z, use_container_width=True)

    # ----------------------------------
    # Summary Metrics
    # ----------------------------------
    def safe_last(series, precision=2):
        s = series.dropna()
        if s.empty:
            return "Not Available"
        return round(s.iloc[-1], precision)

    st.subheader("Summary Statistics")
    st.write({
        "Hedge Ratio (β)": round(beta, 4),
        "Latest Z-Score": safe_last(zscore),
        "Rolling Correlation": safe_last(corr)
    })

    # ----------------------------------
    # Export Data
    # ----------------------------------
    export_df = spread.to_frame("spread")
    export_df["zscore"] = zscore
    export_df["price_A"] = series_a
    export_df["price_B"] = series_b

    st.subheader("📤 Data Export")

    if not export_df.dropna().empty:
        filename = (
            f"analytics_{symbols[0]}_{symbols[1]}_"
            f"{timeframe}_{lookback_minutes}min.csv"
        )

        csv = export_df.dropna().to_csv().encode("utf-8")

        st.download_button(
            label="Download Analytics CSV",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )
    else:
        st.info("⏳ Not enough data available for export yet.")

    # ----------------------------------
    # Alert History
    # ----------------------------------
    st.subheader("🔔 Alert History")

    if st.session_state.alert_history:
        alert_df = pd.DataFrame(st.session_state.alert_history)
        st.dataframe(alert_df, use_container_width=True)
    else:
        st.info("No alerts triggered yet.")
