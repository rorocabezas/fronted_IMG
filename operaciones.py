import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale
 
conn = st.experimental_connection('mysql', type='sql')

@st.cache_data(ttl=3600)
def kpi_ingresos_mes():
    df_ingresos = conn.query("SELECT * FROM KPI_INGRESOS_IMG_MES", ttl=600)
    return df_ingresos

@st.cache_data(ttl=3600)
def qry_branch_offices():
    sucursales = conn.query("SELECT * FROM QRY_BRANCH_OFFICES", ttl=600)
    return sucursales

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)

def calcular_variacion(df, columna_actual, columna_anterior):
    df = df.fillna(0)
    variacion = (df[columna_actual] / df[columna_anterior] - 1) * 100
    variacion = variacion.apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}")
    return variacion

def calcular_ticket_promedio(df, columna_ingresos, columna_tickets):
    df = df.fillna(0)
    ticket_promedio = (df[columna_ingresos] / df[columna_tickets]).round(0)
    return ticket_promedio

df_total = kpi_ingresos_mes()

container = st.container()
with container:
    st.title("GESTION DE OPERACIONES")
    st.markdown("---")
    ### INGRESOS ACTUAL 2023
    df_ingresos_2023 = df_total[(df_total["año"] == 2023)]
    columns_ingresos = ["periodo", "branch_office" , "ticket_number" , "Venta_Neta" , "Venta_SSS" , "Ingresos" , "Ingresos_SSS" ]
    df_ingresos_act = df_ingresos_2023[columns_ingresos]   
    ### INGRESOS ACTUAL 2022
    df_ingresos_2022 = df_total[(df_total["año"] == 2022)]
    df_ingresos_ant = df_ingresos_2022[columns_ingresos]
 
    df_ingresos_actual = df_ingresos_act.rename(columns={"ticket_number": "ticket_number_Act", 
                                        "Venta_Neta" : "Venta_Neta_Act" ,
                                        "Venta_SSS": "Venta_SSS_Act",
                                        "Ingresos" : "Ingresos_Act",
                                        "Ingresos_SSS" : "Ingresos_SSS_Act"})
    
    df_ingresos_anterior = df_ingresos_ant.rename(columns={"ticket_number": "ticket_number_Ant", 
                                            "Venta_Neta" : "Venta_Neta_Ant" ,
                                            "Venta_SSS": "Venta_SSS_Ant",
                                            "Ingresos" : "Ingresos_Ant",
                                            "Ingresos_SSS" : "Ingresos_SSS_Ant"})  
    
    merged_df = df_ingresos_actual.merge(df_ingresos_anterior, on=["branch_office", "periodo"], how="left")

    merged_df = merged_df.assign(
    var_SSS = calcular_variacion(merged_df, 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant'),
    var_Q = calcular_variacion(merged_df, 'ticket_number_Act', 'ticket_number_Ant'),
    ticket_prom_act = calcular_ticket_promedio(merged_df, 'Ingresos_Act', 'ticket_number_Act'),
    ticket_prom_ant = calcular_ticket_promedio(merged_df, 'Ingresos_Ant', 'ticket_number_Ant'))
    merged_df = merged_df.fillna(0)    

    df_sucursales = qry_branch_offices()
    columns_sucursal = ["names", "branch_office" , "principal" , "zone" , "segment"]
    df_sucursales = df_sucursales[columns_sucursal]
    df_sucursales.rename(columns={"names": "supervisor"}, inplace=True)
    final_df = merged_df.merge(df_sucursales, on="branch_office", how="left")
    final_df.rename(columns={"branch_office": "sucursal"}, inplace=True)

    columns_to_show = ['periodo' , 'sucursal' , 'supervisor' , 'Ingresos_Act', 'Ingresos_Ant', 
                       'Venta_Neta_Act', 'Venta_Neta_Ant' , 'ticket_prom_act',  'ticket_prom_ant' ,
                       'var_Q' ,'var_SSS', 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant'] 

    columns_to_show_in_visualization = ['sucursal', 'Ingresos_Act', 'Ingresos_Ant','Venta_Neta_Act', 'Venta_Neta_Ant',
                                        'ticket_prom_act', 'ticket_prom_ant', 'var_Q', 'var_SSS', 
                                        'Ingresos_SSS_Act', 'Ingresos_SSS_Ant']

    df_inicial_display = final_df[columns_to_show_in_visualization].copy()    

    periodos_2023_con_datos = df_total[df_total['año'] == 2023]['periodo'].unique()
    ultimo_periodo = periodos_2023_con_datos[-1]
    periodos_seleccionados_por_defecto = ultimo_periodo

    st.sidebar.title('Filtros Disponibles')    
    periodos = final_df['periodo'].unique()
    supervisors = final_df['supervisor'].unique()
    supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
    branch_offices = final_df[final_df['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
    branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
    periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=periodos_seleccionados_por_defecto)

    if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
        df_filtrado = final_df[
            (final_df['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
            (final_df['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
            (final_df['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)]
        df_filtrado = df_filtrado[columns_to_show]
        columns_to_exclude = ['periodo', 'sucursal', 'supervisor', 'ticket_prom_act', 'ticket_prom_ant', 'var_Q', 'var_SSS']
        sum_total = df_filtrado.drop(columns=columns_to_exclude).sum()
        sum_total_row = pd.Series({'periodo': 'Total', 'sucursal': '', 'supervisor': ''})
        sum_total_row = sum_total_row.append(sum_total)
        df_filtrado = df_filtrado.append(sum_total_row, ignore_index=True)
        # Crea un nuevo DataFrame con las columnas deseadas para df_filtrado
        df_filtrado_display = df_filtrado[columns_to_show_in_visualization].copy()        
    else:
        df_filtrado_display = df_inicial_display.copy()
 
    sum_df_filtrado = df_filtrado_display.sum()
   
    ventas_act_sum = sum_df_filtrado['Venta_Neta_Act']
    ingresos_act_sum = sum_df_filtrado['Ingresos_Act']
    sss_actual_sum = sum_df_filtrado['Ingresos_SSS_Act']    
    ventas_ant_sum = sum_df_filtrado['Venta_Neta_Ant']
    ingresos_ant_sum = sum_df_filtrado['Ingresos_Ant']
    sss_anterior_sum = sum_df_filtrado['Ingresos_SSS_Ant']
    var_sss = (sss_actual_sum/sss_anterior_sum-1) * 100

    ingresos_act = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ingresos_Act'].values[0])
    ingresos_ant = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ingresos_Ant'].values[0])
    var_sss_formatted = format_percentage(var_sss)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="INGRESOS ACTUAL", value=ingresos_act, delta="")
    with col2:
        st.metric(label="INGRESOS ANTERIOR", value=ingresos_ant, delta="")
    with col3:
        st.metric(label="VARIACION % SSS", value=var_sss_formatted, delta="") 

    df_filtrado_display = df_filtrado_display.reset_index(drop=True)
    df_filtrado_display.set_index('sucursal', inplace=True)
    st.dataframe(df_filtrado_display)
    st.markdown("---") 

   