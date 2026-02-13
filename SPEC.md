# Stock Price Prediction App Specification

## Project Overview
- **Name**: StockPredictor
- **Type**: Web Application (Streamlit)
- **Core Functionality**: Predict next day's stock price using historical data from Yahoo Finance
- **Target Users**: Investors and traders seeking quick price predictions

## Technical Stack
- **Language**: Python
- **Data Source**: Yahoo Finance (yfinance library)
- **ML Model**: Random Forest Regressor
- **UI Framework**: Streamlit

## Functionality Specification

### Core Features
1. **Ticker Input**: User enters stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
2. **Data Fetching**: Fetch last 100 days of historical stock data
3. **Price Prediction**: Predict next day's closing price using ML model
4. **Display Results**: Show prediction, current price, and recent trends

### Data Processing
- Features: Open, High, Low, Volume, Close (lagged)
- Target: Next day's Close price
- Train on 80% of data, test on 20%

### User Interface
- Clean, simple input field for ticker
- Display current stock info and price
- Show prediction result prominently
- Show model accuracy metrics

## Acceptance Criteria
- App accepts any valid Yahoo Finance ticker
- Displays prediction for next trading day
- Shows recent price history chart
- Handles errors gracefully (invalid ticker, no data, etc.)
