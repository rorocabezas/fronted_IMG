# Importaciones

import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.dataframe_explorer import dataframe_explorer



# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def ingreso_acum_mes_actual():
    df_acum_mes_actual = conn.query("select * from KPI_INGRESOS_MES", ttl=600)
    return df_acum_mes_actual

st.title("Indicadores JIS Parking")

col1, col2, col3 = st.columns(3)
col1.metric(label="Gain", value=5000, delta=1000)
col2.metric(label="Loss", value=5000, delta=-1000)
col3.metric(label="No Change", value=5000, delta=0)
style_metric_cards()

# Número de filas por página
rows_per_page = 50

# Función para mostrar el DataFrame con paginación
def show_dataframe_with_pagination(df):
    total_rows = len(df)
    num_pages = (total_rows - 1) // rows_per_page + 1

    page_number = st.number_input('Página', min_value=1, max_value=num_pages, value=1)

    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)

    st.dataframe(df[start_idx:end_idx], use_container_width=True, height=600)

df_total = ingreso_acum_mes_actual()

# Crear el DataFrame df_acum_mes con el filtro para el año 2023
df_acum_mes = df_total[df_total['año'] == 2023]

# Crear el DataFrame df_acum_mes_ant con el filtro para el año 2022
df_acum_mes_ant = df_total[df_total['año'] == 2022]


df_acum_mes_ant = df_acum_mes_ant.rename(columns={'ingresos_SSS':'ingresos_sss_anterior',
                                   'venta_SSS':'venta_sss_anterior',
                                   'Trimestre':'trimestre',
                                   'Periodo':'periodo',
                                   'ticket_number':'ticket_anterior'})

df_agrupado = pd.merge(df_acum_mes, df_acum_mes_ant, how='left', left_on=['branch_office', 'periodo'],
                       right_on=['branch_office', 'periodo'], suffixes=('', '_ant'))


# Eliminar las columnas del DataFrame df_acum_mes_ant que se duplicaron en la fusión
df_agrupado = df_agrupado.drop(columns=[ 'id','trimestre_ant', 'period_ant' , 'id_ant', 'año_ant' , 'supervisor_ant'])


# Calcular las nuevas columnas y agregarlas al DataFrame df_agrupado
df_agrupado['var% SSS'] = (df_agrupado['ingresos_SSS'] / df_agrupado['ingresos_sss_anterior'] - 1) * 100
df_agrupado['var Q'] = (df_agrupado['ticket_number'] / df_agrupado['ticket_anterior'] - 1) * 100
df_agrupado['ticket prom act'] = (df_agrupado['ingresos_SSS'] / df_agrupado['ticket_number']).round(0)

# Formatear la columna "var% SSS" con dos decimales y agregar el símbolo "%" y aplicar estilo de color rojo cuando el valor es menor a 0
df_agrupado['var% SSS'] = df_agrupado['var% SSS'].apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}")
df_agrupado['var Q'] = df_agrupado['var Q'].apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}")


# Seleccionar las columnas que deseas mostrar en ambos DataFrames
columns_to_show = ['periodo' , 'branch_office' , 'ticket_number', 'venta_SSS', 'ingresos_SSS', 'ticket_anterior', 'venta_sss_anterior', 'ingresos_sss_anterior', 'var% SSS', 'var Q', 'ticket prom act']

df_inicial = (df_agrupado[columns_to_show].set_index('periodo'))

# Calcular la suma de la columna "ingresos_SSS" en el DataFrame filtrado
ingresos_suma = df_inicial['ingresos_SSS'].sum()

# Obtener una lista de todas los filtros disponibles
periodos = df_agrupado['periodo'].unique()
trimestres = df_agrupado['trimestre'].unique()
supervisors = df_agrupado['supervisor'].unique()

st.sidebar.title('Filtros Disponibles')
#periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos)

supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)

# Filtrar las "branch_office" según el "supervisor" seleccionado
branch_offices = df_agrupado[df_agrupado['supervisor'].isin(supervisor_seleccionados)]['branch_office'].unique()

# Configuración del sidebar branch offices
branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)

trimestre_seleccionados = st.sidebar.multiselect('Seleccione Trimestres:', trimestres)

# Filtrar los "periodo" según el "trimestre" seleccionado
periodos_disponibles = df_agrupado[df_agrupado['trimestre'].isin(trimestre_seleccionados)]['periodo'].unique()

# Configuración del sidebar periodo
periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos_disponibles)

# Filtrar el DataFrame según los filtros seleccionados
if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados or trimestre_seleccionados:
    df_filtrado = df_agrupado[
        (df_agrupado['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
        (df_agrupado['trimestre'].isin(trimestre_seleccionados) if trimestre_seleccionados else True) &
        (df_agrupado['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
        (df_agrupado['branch_office'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)
    ]
else:
    df_filtrado = df_inicial


# Verificar si se han seleccionado opciones para al menos uno de los filtros
if not (periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados or trimestre_seleccionados):
    # Mostrar el DataFrame completo usando st.dataframe
    #st.dataframe(df_agrupado[columns_to_show].set_index('periodo'),use_container_width=True, height=300)
    show_dataframe_with_pagination(df_agrupado[columns_to_show].set_index('periodo'))
else:
    # Si se han seleccionado opciones para al menos uno de los filtros, mostrar el DataFrame filtrado
    st.write('Datos de las opciones seleccionadas:')
    #st.dataframe(df_filtrado[columns_to_show].set_index('periodo'),use_container_width=True, height=300)
    show_dataframe_with_pagination(df_filtrado[columns_to_show].set_index('periodo'))