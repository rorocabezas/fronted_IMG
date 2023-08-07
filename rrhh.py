import streamlit as st
import pandas as pd


# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def rrhh_indicadores():
    df_rrhh = conn.query("select * from KPI_RRHH_MES", ttl=600)
    return df_rrhh

st.title("Indicadores RRHH")

df = rrhh_indicadores()
st.write(df)



st.sidebar.title('Filtros Disponibles')

with st.container():
    st.markdown("""---""")
