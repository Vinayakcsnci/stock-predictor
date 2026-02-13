from flask import Flask, request, jsonify, send_from_directory
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static")


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/service-worker.js")
def service_worker():
    return send_from_directory("static", "service-worker.js")


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    ticker = data.get("ticker", "").upper()

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="100d")

        if df.empty:
            return jsonify({"error": f"No data found for {ticker}"})

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
            return jsonify({"error": "Not enough data"})

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

        latest = df.iloc[-1]
        X_pred = scaler.transform([latest[features].values])
        prediction = model.predict(X_pred)[0]

        current_price = float(df["Close"].iloc[-1])
        change = ((prediction - current_price) / current_price) * 100

        dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()[-30:]
        prices = df["Close"].tolist()[-30:]

        next_day = (df["Date"].iloc[-1] + timedelta(days=1)).strftime("%Y-%m-%d")

        return jsonify(
            {
                "current_price": current_price,
                "prediction": float(prediction),
                "change": float(change),
                "dates": dates,
                "prices": prices,
                "prediction_date": next_day,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
