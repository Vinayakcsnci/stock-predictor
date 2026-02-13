import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="StockPredictor", page_icon="📈", layout="centered")

st.markdown(
    """
<style>
    .stTextInput > div > div > input {
        font-size: 18px;
    }
    .stButton > button {
        width: 100%;
        font-size: 18px;
    }
    div[data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("📈 Stock Price Predictor")
st.markdown("Predict next day's closing price using Machine Learning")

ticker_input = st.text_input(
    "Enter Stock Ticker", placeholder="e.g., AAPL, GOOGL, MSFT"
).upper()

if st.button("Predict", type="primary"):
    if not ticker_input:
        st.error("Please enter a stock ticker")
    else:
        with st.spinner("Fetching data and making prediction..."):
            try:
                stock = yf.Ticker(ticker_input)
                df = stock.history(period="100d")

                if df.empty:
                    st.error(f"No data found for ticker '{ticker_input}'")
                else:
                    df = df.reset_index()

                    df["Prev_Close"] = df["Close"].shift(1)
                    df["Prev_Open"] = df["Open"].shift(1)
                    df["Prev_High"] = df["High"].shift(1)
                    df["Prev_Low"] = df["Low"].shift(1)
                    df["Prev_Volume"] = df["Volume"].shift(1)
                    df["MA_5"] = df["Close"].rolling(window=5).mean()
                    df["MA_10"] = df["Close"].rolling(window=10).mean()

                    df = df.dropna()

                    if len(df) < 30:
                        st.error("Not enough data for prediction")
                    else:
                        features = [
                            "Prev_Close",
                            "Prev_Open",
                            "Prev_High",
                            "Prev_Low",
                            "Prev_Volume",
                            "MA_5",
                            "MA_10",
                        ]
                        X = df[features]
                        y = df["Close"]

                        split_idx = int(len(X) * 0.8)
                        X_train, X_test = X[:split_idx], X[split_idx:]
                        y_train, y_test = y[:split_idx], y[split_idx:]

                        scaler = StandardScaler()
                        X_train_scaled = scaler.fit_transform(X_train)
                        X_test_scaled = scaler.transform(X_test)

                        model = RandomForestRegressor(n_estimators=100, random_state=42)
                        model.fit(X_train_scaled, y_train)

                        score = model.score(X_test_scaled, y_test)

                        latest = df.iloc[-1]
                        X_pred = scaler.transform([latest[features].values])
                        prediction = model.predict(X_pred)[0]

                        current_price = df["Close"].iloc[-1]
                        price_change = (
                            (prediction - current_price) / current_price
                        ) * 100

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Current Price", f"${current_price:.2f}")
                        col2.metric(
                            "Predicted Price",
                            f"${prediction:.2f}",
                            f"{price_change:+.2f}%",
                        )
                        col3.metric("Model Accuracy", f"{score * 100:.1f}%")

                        st.subheader(f"{ticker_input} - Last 30 Days")
                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatter(
                                x=df["Date"].iloc[-30:],
                                y=df["Close"].iloc[-30:],
                                mode="lines+markers",
                                name="Actual",
                                line=dict(color="#00CC96", width=2),
                            )
                        )
                        fig.add_trace(
                            go.Scatter(
                                x=[df["Date"].iloc[-1] + timedelta(days=1)],
                                y=[prediction],
                                mode="markers",
                                name="Prediction",
                                marker=dict(color="#EF553B", size=12, symbol="diamond"),
                            )
                        )
                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            template="plotly_dark",
                            height=350,
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.success(
                            f"Prediction complete! {ticker_input} next day price is estimated at ${prediction:.2f}"
                        )

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("📊 Data provided by Yahoo Finance | ML Model: Random Forest")
