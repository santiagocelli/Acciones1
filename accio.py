# app.py
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import mplfinance as mpf
import yfinance as yf
import ta

def fetch_sp500_data():
    """Web scrapes S&P 500 data."""
    url = "https://finance.yahoo.com/quote/%5EGSPC/components/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    df = pd.read_html(str(table))[0]
    return df

def fetch_merval_data():
    """Web scrapes Merval data."""
    url = "https://es.investing.com/indices/merval-components"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"class": "genTbl"})
    df = pd.read_html(str(table))[0]
    return df

def fetch_stock_data(ticker, period="6mo", interval="1d"):
    """Fetch historical data for a stock using Yahoo Finance."""
    data = yf.download(ticker, period=period, interval=interval)
    data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()
    data["MACD"], data["Signal"] = ta.trend.MACD(data["Close"]).macd_signal()
    data["SMA_20"] = ta.trend.SMAIndicator(data["Close"], window=20).sma_indicator()
    data["SMA_50"] = ta.trend.SMAIndicator(data["Close"], window=50).sma_indicator()
    return data

# Streamlit Application
def main():
    st.title("Indicadores de Acciones - S&P 500 y Merval")
    st.sidebar.title("Opciones")

    # Fetch data
    st.sidebar.text("Cargando datos...")
    sp500_data = fetch_sp500_data()
    merval_data = fetch_merval_data()

    # Menu Selection
    index_option = st.sidebar.selectbox("Seleccione un índice", ["S&P 500", "Merval"])
    
    if index_option == "S&P 500":
        st.header("S&P 500")
        ticker = st.sidebar.selectbox("Seleccione una acción", sp500_data["Symbol"].tolist())
    elif index_option == "Merval":
        st.header("Merval")
        ticker = st.sidebar.selectbox("Seleccione una acción", merval_data["Ticker"].tolist())
    
    # Fetch and Display Stock Data
    st.write(f"Mostrando datos para: {ticker}")
    period = st.sidebar.selectbox("Seleccione el período", ["1mo", "3mo", "6mo", "1y", "5y"])
    interval = st.sidebar.selectbox("Seleccione el intervalo", ["1d", "1wk", "1mo"])

    stock_data = fetch_stock_data(ticker, period=period, interval=interval)

    # Display OHLC Data
    st.write("Datos históricos (OHLC):")
    st.dataframe(stock_data.tail(10))

    # Display Candle Chart with Indicators
    st.write("Gráfico de Velas con Indicadores:")
    fig, ax = mpf.plot(
        stock_data,
        type="candle",
        mav=(20, 50),  # Simple moving averages
        volume=True,
        returnfig=True,
        style="yahoo"
    )
    st.pyplot(fig)

    # Additional Indicators
    st.write("Indicadores Técnicos:")
    st.line_chart(stock_data[["RSI", "MACD", "Signal"]])

if __name__ == "__main__":
    main()
