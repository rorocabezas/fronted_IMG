# Importaciones

import streamlit as st
import pandas as pd


from streamlit_extras.metric_cards import style_metric_cards


# Importación Boostrap
st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">', unsafe_allow_html=True)

st.markdown("""
<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">Navbar</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="#">Home</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">Indicadores</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">Dashboard</a>
        </li>
      </ul>
    </div>
  </div>
</nav>
""", unsafe_allow_html=True)

# Inicializacion de conexion.
conn = st.experimental_connection('mysql', type='sql')


@st.cache_data_actual(ttl=600)
def ingreso_acum_mes_actual():
    df_acum_mes_actual = conn.query("""
    SELECT
	  KPI_INGRESOS_ACTUAL_MES.Periodo, 
	  KPI_INGRESOS_ACTUAL_MES.period, 
	  KPI_INGRESOS_ACTUAL_MES.Trimestre, 
	  KPI_INGRESOS_ACTUAL_MES.`Año`, 
	  KPI_INGRESOS_ACTUAL_MES.branch_office, 
	  KPI_INGRESOS_ACTUAL_MES.supervisor, 
	  KPI_INGRESOS_ACTUAL_MES.ticket_number, 
	  KPI_INGRESOS_ACTUAL_MES.Venta_SSS, 
	  KPI_INGRESOS_ACTUAL_MES.Ingresos_SSS
    FROM 	KPI_INGRESOS_ACTUAL_MES
    LIMIT 999 """, ttl=600)
    return df_acum_mes_actual

@st.cache_data_anterior(ttl=600)
def ingreso_acum_mes_anterior():
    df_acum_mes_anterior = conn.query("""
    SELECT
	  KPI_INGRESOS_ANTERIOR_MES.Periodo, 
	  #KPI_INGRESOS_ANTERIOR_MES.period, 
	  #KPI_INGRESOS_ANTERIOR_MES.Trimestre, 
	  KPI_INGRESOS_ANTERIOR_MES.`Año`, 
	  KPI_INGRESOS_ANTERIOR_MES.branch_office, 
	  #KPI_INGRESOS_ANTERIOR_MES.supervisor, 
	  KPI_INGRESOS_ANTERIOR_MES.ticket_number as ticket_anterior, 
	  KPI_INGRESOS_ANTERIOR_MES.Venta_SSS as ventas_sss_anterior, 
	  KPI_INGRESOS_ANTERIOR_MES.Ingresos_SSS as ingresos_sss_anterior
    FROM
	  KPI_INGRESOS_ANTERIOR_MES
    LIMIT 999""", ttl=600)
    return df_acum_mes_anterior

st.title("Indicadores JIS Parking")

col1, col2, col3 = st.columns(3)
col1.metric(label="Gain", value=5000, delta=1000)
col2.metric(label="Loss", value=5000, delta=-1000)
col3.metric(label="No Change", value=5000, delta=0)
style_metric_cards()


df_acum_mes = ingreso_acum_mes_actual()
#st.dataframe(df_acum_mes, height=400)

df_acum_mes_ant = ingreso_acum_mes_anterior()
#st.dataframe(df_acum_mes_ant, height=400)


df_agrupado = pd.merge(df_acum_mes, df_acum_mes_ant, how='left', left_on=['branch_office', 'Periodo'], right_on=['branch_office', 'Periodo'])
df_agrupado[['Periodo','Trimestre','branch_office','supervisor','ticket_number','Venta_SSS', 'Ingresos_SSS', 'ticket_anterior', 'ventas_sss_anterior' , 'ingresos_sss_anterior']]








df_agrupado.head(50)
st.dataframe(df_agrupado, height=400)





