import streamlit as st
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import ta

# Función para obtener lista de empresas del S&P 500
def fetch_sp500_list():
    """Obtiene la lista de empresas del S&P 500 desde Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500 = pd.read_html(url)[0]
    return sp500["Symbol"].tolist()

# Función para obtener lista de empresas del Merval
def fetch_merval_list():
    """Lista predefinida de empresas del Merval."""
    # Aquí se puede usar scraping o una API para obtener la lista actualizada.
    return ["GGAL.BA", "YPF.BA", "PAMP.BA", "TXAR.BA", "BMA.BA"]

# Función para obtener datos históricos de acciones
def fetch_stock_data(ticker, period="6mo", interval="1d"):
    """Obtiene datos históricos de Yahoo Finance."""
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        st.error(f"No se encontraron datos históricos para {ticker}.")
        return pd.DataFrame()
    # Calcular indicadores técnicos
    data["RSI"] = ta.momentum.RSIIndicator(data["Close"]).rsi()
    data["MACD"], data["Signal"] = ta.trend.MACD(data["Close"]).macd_signal()
    data["SMA_20"] = ta.trend.SMAIndicator(data["Close"], window=20).sma_indicator()
    data["SMA_50"] = ta.trend.SMAIndicator(data["Close"], window=50).sma_indicator()
    return data

# Aplicación principal de Streamlit
def main():
    st.title("Indicadores de Acciones - S&P 500 y Merval")
    st.sidebar.title("Opciones")

    # Opciones de índices
    index_option = st.sidebar.selectbox("Seleccione un índice", ["S&P 500", "Merval"])
    period = st.sidebar.selectbox("Seleccione el período", ["1mo", "3mo", "6mo", "1y", "5y"])
    interval = st.sidebar.selectbox("Seleccione el intervalo", ["1d", "1wk", "1mo"])

    # Listar acciones según el índice seleccionado
    if index_option == "S&P 500":
        tickers = fetch_sp500_list()
    elif index_option == "Merval":
        tickers = fetch_merval_list()

    # Seleccionar acción
    ticker = st.sidebar.selectbox("Seleccione una acción", tickers)
    st.write(f"Mostrando datos para: {ticker}")

    # Obtener datos históricos
    stock_data = fetch_stock_data(ticker, period=period, interval=interval)

    if stock_data.empty:
        return

    # Mostrar datos históricos
    st.write("Datos históricos (OHLC):")
    st.dataframe(stock_data.tail(10))

    # Mostrar gráfico de velas con indicadores técnicos
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

    # Mostrar indicadores técnicos adicionales
    st.write("Indicadores Técnicos:")
    st.line_chart(stock_data[["RSI", "MACD", "Signal"]])

if __name__ == "__main__":
    main()
