# app.py
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

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
        st.dataframe(sp500_data)

        # Ticker Selection
        ticker = st.sidebar.selectbox("Seleccione una acción", sp500_data["Symbol"])
        ticker_data = sp500_data[sp500_data["Symbol"] == ticker]
        st.write(f"Datos de {ticker}")
        st.table(ticker_data)

    elif index_option == "Merval":
        st.header("Merval")
        st.dataframe(merval_data)

        # Ticker Selection
        ticker = st.sidebar.selectbox("Seleccione una acción", merval_data["Ticker"])
        ticker_data = merval_data[merval_data["Ticker"] == ticker]
        st.write(f"Datos de {ticker}")
        st.table(ticker_data)

if __name__ == "__main__":
    main()
