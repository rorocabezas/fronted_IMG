import streamlit as st
import pandas as pd

# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def eerr():
    df_eerr = conn.query("SELECT * FROM QRY_TP_EERR WHERE `Año` = 2023 and Grupo <> '90 - Extras' and Sucursal <>  'Ajuste COQUIMBO'", ttl=600)
    return df_eerr

df = eerr()



resultado = df.pivot_table(index='Grupo', columns='Meses', values='Monto', aggfunc='sum')
resultado.loc['Resultado Operacional'] = resultado.sum()
# Obtener los valores del grupo 10 - INGRESOS para cada mes
ingresos = resultado.loc['10 - INGRESOS']

# Calcular el porcentaje de cada grupo respecto a los ingresos y agregarlo como nuevas columnas
for mes in ingresos.index:
    resultado[mes + ' %'] = round((resultado[mes] / ingresos[mes]) * 100, 2).apply(lambda x: f'{x:.2f}%')

# Reordenar las columnas
column_order = []
for mes in ingresos.index:
    column_order.append(mes)
    column_order.append(mes + ' %')
resultado = resultado[column_order]

# Ordenar las filas alfabéticamente
resultado = resultado.sort_index()


st.sidebar.title('Filtros Disponibles')
periodos = df['Meses'].unique()
supervisor = df['Supervisor'].unique()
sucursal = df['Sucursal'].unique()

periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos)
supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisor)
branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', sucursal)



# Mostrar el resultado
st.dataframe(resultado)





