import pandas as pd
import yfinance as yf
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("stockdata-e9bda-firebase-adminsdk-csce0-910b1153c2.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fetch the S&P 100 list from Wikipedia
def get_top_100_tickers():
    url = "https://en.wikipedia.org/wiki/S%26P_100"
    tables = pd.read_html(url)
    sp100 = tables[2]  # Table with S&P 100 companies
    data = sp100["Symbol"].tolist()
    return data

# Fetch stock price using Yahoo Finance
def fetch_stock_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if not data.empty:
        return data['Close'].iloc[-1]
    else:
        return None

# Fetch market cap and stock name for a list of tickers
def fetch_market_cap_and_name(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get("marketCap", None)
        stock_name = info.get("shortName", "N/A")  # Get the full company name
        current_price = fetch_stock_price(ticker)
        if market_cap:
            data.append({"Ticker": ticker, "Stock Name": stock_name, "Market Cap": market_cap, "Current Price": current_price})
    return pd.DataFrame(data)

# Write data to Firestore
def write_to_firestore(tickers):
    stock_data = fetch_market_cap_and_name(tickers)
    
    # Loop through the DataFrame rows and write to Firestore
    for index, row in stock_data.iterrows():  # Use iterrows to loop through DataFrame rows
        stock = row.to_dict()  # Convert the row to a dictionary
        doc_ref = db.collection('stocks').document(stock["Ticker"])  # Use the Ticker as document ID
        doc_ref.set(stock)  # Write data to Firestore
        print(f"Data for {stock['Ticker']} written successfully!")

# Main script
tickers = get_top_100_tickers()
write_to_firestore(tickers)






