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
    return ["GGAL.BA", "YPF.BA", "PAMP.BA", "TXAR.BA", "BMA.BA"]

# Función para obtener datos históricos de acciones
def fetch_stock_data(ticker, period="6mo", interval="1d"):
    """Obtiene datos históricos de Yahoo Finance y calcula indicadores técnicos."""
    data = yf.download(ticker, period=period, interval=interval)

    if data.empty:
        st.error(f"No se encontraron datos históricos para {ticker}.")
        return pd.DataFrame()

    # Validar columnas requeridas
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.error(f"Faltan las siguientes columnas en los datos: {missing_columns}")
        return pd.DataFrame()

    # Validar y convertir datos a numérico
    for col in required_columns:
        if col in data.columns:  # Asegurar que la columna existe
            # Reemplazo: Verificar si todos los valores son nulos de manera segura
            if data[col].isna().sum() == len(data[col]):  # Comparar el total de nulos con el tamaño
                st.error(f"La columna {col} contiene solo valores nulos.")
                return pd.DataFrame()
            try:
                data[col] = pd.to_numeric(data[col], errors="coerce")  # Convertir a numérico
            except Exception as e:
                st.error(f"Error al convertir la columna {col} a numérico: {e}")
                return pd.DataFrame()

    # Calcular indicadores técnicos
    try:
        close_series = data["Close"]

        # RSI
        rsi_indicator = ta.momentum.RSIIndicator(close_series)
        data["RSI"] = rsi_indicator.rsi()

        # MACD
        macd_indicator = ta.trend.MACD(close_series)
        data["MACD"] = macd_indicator.macd()
        data["Signal"] = macd_indicator.macd_signal()

        # Medias móviles
        sma_20 = ta.trend.SMAIndicator(close_series, window=20)
        sma_50 = ta.trend.SMAIndicator(close_series, window=50)
        data["SMA_20"] = sma_20.sma_indicator()
        data["SMA_50"] = sma_50.sma_indicator()
    except Exception as e:
        st.error(f"Error al calcular indicadores técnicos: {e}")
        return pd.DataFrame()

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

    # Validar columnas para mplfinance
    required_columns = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in stock_data.columns for col in required_columns):
        st.error(f"Faltan columnas necesarias para el gráfico: {required_columns}")
        return

    # Mostrar gráfico de velas con indicadores técnicos
    st.write("Gráfico de Velas con Indicadores:")
    try:
        fig, ax = mpf.plot(
            stock_data,
            type="candle",
            mav=(20, 50),  # Simple moving averages
            volume=True,
            returnfig=True,
            style="yahoo"
        )
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error al generar el gráfico de velas: {e}")

    # Mostrar indicadores técnicos adicionales
    st.write("Indicadores Técnicos:")
    st.line_chart(stock_data[["RSI", "MACD", "Signal"]])

if __name__ == "__main__":
    main()
