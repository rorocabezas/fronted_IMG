# Importaciones

import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards


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

# Seleccionar las columnas que deseas mostrar en ambos DataFrames
columns_to_show = ['periodo' , 'branch_office' , 'ticket_number', 'venta_SSS', 'ingresos_SSS', 'ticket_anterior', 'venta_sss_anterior', 'ingresos_sss_anterior']

df_inicial = (df_agrupado[columns_to_show].set_index('periodo'))

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
    st.dataframe(df_agrupado[columns_to_show].set_index('periodo'), height=400)
else:
    # Si se han seleccionado opciones para al menos uno de los filtros, mostrar el DataFrame filtrado
    st.write('Datos de las opciones seleccionadas:')
    st.dataframe(df_filtrado[columns_to_show].set_index('periodo'), height=400)

