# Importaciones

import streamlit as st
import pandas as pd
import locale



# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')



@st.cache_data(ttl=3600)
def ingreso_acum_mes_actual():
    df_acum_mes_actual = conn.query("select * from KPI_INGRESOS_MES", ttl=600)
    return df_acum_mes_actual

# Número de filas por página
rows_per_page = 20

# Función para mostrar el DataFrame con paginación
def show_dataframe_with_pagination(df):
    total_rows = len(df)
    num_pages = (total_rows - 1) // rows_per_page + 1

    page_number = st.number_input('Página', min_value=1, max_value=num_pages, value=1)

    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)

    st.dataframe(df[start_idx:end_idx], use_container_width=True)

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


df_agrupado = df_agrupado.rename(columns={
    'periodo': 'periodo',
    'branch_office': 'sucursal',
    'ticket_number': 'ticket act',
    'venta_SSS': 'ventas act',
    'ingresos_SSS': 'ingresos act',
    'ticket_anterior': 'ticket ant',
    'venta_sss_anterior': 'ventas ant',
    'ingresos_sss_anterior': 'ingresos ant'
})

# Seleccionar las columnas que deseas mostrar en ambos DataFrames
columns_to_show = ['periodo' , 'sucursal' , 'ticket act', 'ventas act', 'ingresos act', 'ticket ant', 'ventas ant', 'ingresos ant', 'var% SSS', 'var Q', 'ticket prom act']

# Seleccionar las columnas que deseas mostrar en ambos DataFrames
#columns_to_show = ['periodo' , 'branch_office' , 'ticket_number', 'venta_SSS', 'ingresos_SSS', 'ticket_anterior', 'venta_sss_anterior', 'ingresos_sss_anterior', 'var% SSS', 'var Q', 'ticket prom act']

# Ahora puedes usar la lista actualizada para seleccionar las columnas del DataFrame
df_inicial = df_agrupado[columns_to_show].set_index('periodo')

# Obtener una lista de todas los filtros disponibles
periodos = df_agrupado['periodo'].unique()
trimestres = df_agrupado['trimestre'].unique()
supervisors = df_agrupado['supervisor'].unique()

st.sidebar.title('Filtros Disponibles')
#periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos)

supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)

# Filtrar las "branch_office" según el "supervisor" seleccionado
branch_offices = df_agrupado[df_agrupado['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()

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
        (df_agrupado['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)
    ]
else:
    df_filtrado = df_inicial

# Creamos un DataFrame agrupado con la sumatoria total de cada columna de df_filtrado
sum_df_filtrado = df_filtrado.sum()

# Función para formatear un número como moneda con símbolo de dólar y separadores de miles
def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)

# Obtener las sumatorias de las columnas requeridas
ticket_act_sum = sum_df_filtrado['ticket act']
ventas_act_sum = sum_df_filtrado['ventas act']
ingresos_act_sum = sum_df_filtrado['ingresos act']
ticket_ant_sum = sum_df_filtrado['ticket ant']
ventas_ant_sum = sum_df_filtrado['ventas ant']
ingresos_ant_sum = sum_df_filtrado['ingresos ant']
var_sss = (ingresos_act_sum/ingresos_ant_sum-1) * 100

# Formatear las sumatorias de ingresos a formato de moneda
ingresos_act_sum_formatted = format_currency(ingresos_act_sum)
ingresos_ant_sum_formatted = format_currency(ingresos_ant_sum)
var_sss_formatted = format_percentage(var_sss)


# Título principal
# Título principal con formato HTML
st.markdown("""
    <div class="mx-10 mt-5">
        <h1 class="text-6xl ">Indicadores JIS Parking</h1>
    </div>
""", unsafe_allow_html=True)


# Contenido de la primera tarjeta "Ingresos Actual"

col1, col2, col3 = st.columns(3)
    
with col1:
    st.markdown(f"""
    <link href="https://unpkg.com/tailwindcss@2.2.4/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://demos.creative-tim.com/notus-js/assets/vendor/@fortawesome/fontawesome-free/css/all.min.css" rel="stylesheet">
         <div class="px-1 pt-4 pb5">
            <!---== primero     Stats Container ====--->
            <div class="flex flex-col xl:flex-row shadow hover:shadow-md w-full bg-white rounded-lg overflow-hidden cursor-pointer">
                <div class="w-72 bg-white max-w-xs mx-auto rounded-sm overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 transform hover:scale-100 cursor-pointer">
                    <div class="h-20 bg-green-400 flex items-center justify-between">
                        <p class="mr-0 text-white text-lg pl-5">INGRESOS ACTUAL</p>
                    </div>
                <div class="flex justify-between px-5 pt-6 mb-2 text-sm text-gray-600">
                <p>Venta Neta + Abonados</p>
            </div>
                <p class="py-4 text-3xl ml-5">{ingresos_act_sum_formatted}</p>
                <!-- <hr > -->
        </div>
    </div>   
</div>
""", unsafe_allow_html=True)

# Contenido de la segunda tarjeta "Ingresos Anterior"
    with col2:
        st.markdown(f"""
    <link href="https://unpkg.com/tailwindcss@2.2.4/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://demos.creative-tim.com/notus-js/assets/vendor/@fortawesome/fontawesome-free/css/all.min.css" rel="stylesheet">
       <div class="px-1 pt-4 pb5">
            <!---== Segunda   Stats Container ====--->
            <div class="flex flex-col xl:flex-row shadow hover:shadow-md w-full bg-white rounded-lg overflow-hidden cursor-pointer">
                <div class="w-72 bg-white max-w-xs mx-auto rounded-sm overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 transform hover:scale-100 cursor-pointer">
                    <div class="h-20 bg-red-400 flex items-center justify-between">
                        <p class="mr-0 text-white text-lg pl-5">INGRESOS ANTERIOR</p>
                    </div>
                <div class="flex justify-between px-5 pt-6 mb-2 text-sm text-gray-600">
                <p>Venta Neta + Abonados</p>
            </div>
                <p class="py-4 text-3xl ml-5">{ingresos_ant_sum_formatted}</p>
                <!-- <hr > -->
        </div>
    </div>   
</div>
""", unsafe_allow_html=True)

# Contenido de la tercera tarjeta "Var SSS"
    with col3:
        st.markdown(f"""
    <link href="https://unpkg.com/tailwindcss@2.2.4/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://demos.creative-tim.com/notus-js/assets/vendor/@fortawesome/fontawesome-free/css/all.min.css" rel="stylesheet">
        <div class="px-1 pt-4 pb5">
            <!---== Tercera Stats Container ====--->
            <div class="flex flex-col xl:flex-row shadow hover:shadow-md w-full bg-white rounded-lg overflow-hidden cursor-pointer">
                <div class="w-72 bg-white max-w-xs mx-auto rounded-sm overflow-hidden shadow-lg hover:shadow-2xl transition duration-500 transform hover:scale-100 cursor-pointer">
                    <div class="h-20 bg-blue-400 flex items-center justify-between">
                        <p class="mr-0 text-white text-lg pl-5">VARIACION % SSS</p>
                    </div>
                <div class="flex justify-between px-5 pt-6 mb-2 text-sm text-gray-600">
                <p>Same Store Sale</p>
            </div>
                <p class="py-4 text-3xl ml-5">{var_sss_formatted}</p>
                <!-- <hr > -->
        </div>
    </div>   
</div>
""", unsafe_allow_html=True)


#col1.hasClicked = card(
#    title="Ingresos Totales",
#    text=ingresos_act_sum_formatted,
#    image=""
#    )

# Verificar si se han seleccionado opciones para al menos uno de los filtros
with st.container():
    if not (periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados or trimestre_seleccionados):
        st.write('Datos sin selección:')
        show_dataframe_with_pagination(df_agrupado[columns_to_show].set_index('periodo'))
        # Si se han seleccionado opciones para al menos uno de los filtros, mostrar el DataFrame filtrado
    else:
        st.write('Datos de las opciones seleccionadas:')
        #st.dataframe(df_filtrado[columns_to_show].set_index('periodo'),use_container_width=True, height=300)
        show_dataframe_with_pagination(df_filtrado[columns_to_show].set_index('periodo'))


