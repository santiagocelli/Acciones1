def fetch_sp500_data():
    """Web scrapes S&P 500 data."""
    url = "https://finance.yahoo.com/quote/%5EGSPC/components/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")
    
    if not table:
        st.error("No se encontró la tabla en la página web de S&P 500.")
        return pd.DataFrame()  # Devuelve un DataFrame vacío si no hay tabla

    df = pd.read_html(str(table))[0]

    # Verificar si la columna 'Symbol' existe
    if "Symbol" not in df.columns:
        st.warning("La columna 'Symbol' no se encuentra en los datos.")
        st.write("Columnas disponibles:", df.columns)
        return pd.DataFrame()  # Devuelve un DataFrame vacío si falta la columna

    return df
Manejo de errores en la función main:
Asegúrate de que el programa valida si sp500_data tiene contenido antes de proceder:

python
Copiar código
def main():
    st.title("Indicadores de Acciones - S&P 500 y Merval")
    st.sidebar.title("Opciones")

    # Fetch data
    st.sidebar.text("Cargando datos...")
    sp500_data = fetch_sp500_data()
    merval_data = fetch_merval_data()

    if sp500_data.empty:
        st.error("No se pudieron cargar los datos de S&P 500. Intenta más tarde.")
        return
    if merval_data.empty:
        st.error("No se pudieron cargar los datos de Merval. Intenta más tarde.")
        return

    # Menu Selection
    index_option = st.sidebar.selectbox("Seleccione un índice", ["S&P 500", "Merval"])
    
    if index_option == "S&P 500":
        st.header("S&P 500")
        st.write("Estructura de los datos:")
        st.dataframe(sp500_data)

        # Validar existencia de la columna antes de mostrar el selector
        if "Symbol" in sp500_data.columns:
            ticker = st.sidebar.selectbox("Seleccione una acción", sp500_data["Symbol"].tolist())
            st.write(f"Mostrando datos para: {ticker}")
        else:
            st.error("No se encontró la columna 'Symbol' en los datos de S&P 500.")

    elif index_option == "Merval":
        st.header("Merval")
        st.dataframe(merval_data)

        if "Ticker" in merval_data.columns:
            ticker = st.sidebar.selectbox("Seleccione una acción", merval_data["Ticker"].tolist())
            st.write(f"Mostrando datos para: {ticker}")
        else:
            st.error("No se encontró la columna 'Ticker' en los datos de Merval.")
