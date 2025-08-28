import pandas as pd
import plotly.express as px
import streamlit as st 
import mysql.connector as connection
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import requests
import json

st.set_page_config(
  page_title="Dashboard Curso CPCE Catamarca 08-2025",
  page_icon=":bar_chart:",
  layout="wide"                 
)

@st.cache_data

# Si quiero obtener los datos desde un Excel
def get_data_from_excel():
  df = pd.read_excel(
    io='master_ventas.xlsx',
    engine='openpyxl',
  )
  df['fecha'] = pd.to_datetime(df['fecha'])
  df['periodo'] = pd.to_datetime(df['periodo'])
  return df

# Si quiero obtener los datos desde una base de datos MySQL
def get_data_from_mysql():
  try:
    print(f"EMPRESA: {empresa}")
    if (empresa != None):
      mydb = connection.connect(host="localhost", database = empresa, user="root", passwd="root", use_pure=True)
      query = "SELECT * FROM vta_comprobante;"
      df = pd.read_sql(query,mydb)
      df['fecha'] = pd.to_datetime(df['fecha'])
      df['periodo'] = pd.to_datetime(df['periodo'])
      mydb.close()
    else:
      df = pd.DataFrame()
  except Exception as e:
    mydb.close()
    print(str(e))
  return df

categoria_contribuyente = ""

# En el archivo "secrets.json" guardo los datos secretos de mi cuenta en la API
# de Agustín Bustos Piasentini (ustedes deberían utilizar los de su propia cuenta)
with open('secrets.json', 'r') as f:
  secrets = json.load(f)
api_key = secrets.get('API_KEY')
api_user = secrets.get('API_USER')

# Armo una barra lateral con los filtros
st.sidebar.header("Filtros")

# Diccionario con las empresas (esto podría sacarlo de la misma base de datos MySQL)
dict_empresas = { 
                'fernandezdario': '20274025493',
                'master': '27119206478'
                }

# Filtro para seleccionar la empresa (en nuestro caso 2 solamente)
empresa = st.sidebar.selectbox(
    "Empresa",
    dict_empresas.keys()
)

# Obtengo los datos del padrón de ARCA sobre la CUIT de la empresa seleccionada
# usando la API de Agustín Bustos Piasentini
# http://api-constancias-de-inscripcion.mrbot.com.ar/
constancia = requests.get("https://api-constancias-de-inscripcion.mrbot.com.ar/consulta_constancia/",
                          params={"cuit": dict_empresas[empresa],
                                  "usuario": api_user,
                                  "api_key": api_key})
# Me devuelve un JSON
respuesta_json = constancia.json()
#print(respuesta_json["datosMonotributo"])
# Busco si tengo el objeto "datosMonotributo"
# Si existe, ya sé que es monotributista, entonces voy por el objeto "categoriaMonotributo"
# y dentro de él, tengo un par ("descripcionCategoria"), que me va a indicar (precisamente) la categoría
if (respuesta_json["datosMonotributo"] is None):
  # No es monotributista
  categoria_contribuyente = ""
else:
  # Es monotributista, extraigo la categoría
  categoria_contribuyente = respuesta_json["datosMonotributo"]["categoriaMonotributo"]["descripcionCategoria"][0:1]
  #print(f"Categoria contribuyente: {categoria_contribuyente}")

# Elijo uno de los 2 métodos (Excel o MySQL) para alimentar el dashboard
#df=get_data_from_excel()
df=get_data_from_mysql()

# Filtro para fecha desde
fecha_desde = st.sidebar.date_input(
  "Fecha desde",
  df["fecha"].unique().min()
)

# Filtro para fecha hasta
fecha_hasta = st.sidebar.date_input(
  "Fecha hasta",
  df["fecha"].unique().max()
)

# Filtro para campo provincia
provincia = st.sidebar.multiselect(
  "Provincia:",
  options=df["provincia"].unique(),
  default=df["provincia"].unique()
)

# Filtro para cliente
cliente = st.sidebar.multiselect(
  "Cliente:",
  options=df["cliente"].unique(),
  default=df["cliente"].unique()
)

# Filtro para condición de venta
condicion_venta = st.sidebar.multiselect(
  "Condición de venta:",
  options=df["condicion_venta"].unique(),
  default=df["condicion_venta"].unique()
)

# Filtro para sucursal
sucursal = st.sidebar.multiselect(
  "Sucursal:",
  options=df["sucursal"].unique(),
  default=df["sucursal"].unique()
)

# Filtro para trabajdor
trabajador = st.sidebar.multiselect(
  "Trabajador:",
  options=df["trabajador"].unique(),
  default=df["trabajador"].unique()
)

# Con esta query, filtro los datos que leí del origen (Excel o MySQL), según
# los filtros aplicados arriba
df_filtrado = df.query(
  "provincia==@provincia & cliente==@cliente & condicion_venta==@condicion_venta & sucursal==@sucursal & trabajador==@trabajador & fecha>=@fecha_desde & fecha<=@fecha_hasta"
)

# Página principal
# Título
st.subheader(f":bar_chart: Dashboard ventas - {dict_empresas[empresa]}")

# El dashboard propiamente dicho

# Agrupo por el campo "periodo" las ventas (que, como son a nivel factura, pueden existir
# varias para un mismo período), sumando el campo "total"
# Finalmente las ordeno por el campo "periodo"
ventas_por_periodo = (
  df_filtrado.groupby(by=["periodo"]).sum(numeric_only=True)[["total"]].sort_values(by="periodo")
)
# Creo un campo "acumulado" dentro del DataFrame, que vaya acumulando las ventas
# en cada período, con los anteriores (es lo que me va a servir para ver si
# el contribuyente viene dentro de los parámetros de facturación de una categoría)
ventas_por_periodo['acumulado'] = ventas_por_periodo['total'].cumsum()

# Creo una "Figure" y agrego dos "trace" (uno con ventas por período y el otro con el acumulado)
fig = go.Figure()
fig.add_trace(go.Scatter(x=ventas_por_periodo.index, y=ventas_por_periodo['total'],
                    mode='lines+markers',
                    name='Mensuales'))
fig.add_trace(go.Scatter(x=ventas_por_periodo.index, y=ventas_por_periodo['acumulado'],
                    mode='lines+markers',
                    name='Acumuladas'))

# Trazo las lineas horizontales de las categorias de monotributo
# Uso la capacidad de Pandas de scrappear una web, detectar tablas y
# convertirlas en un DataFrame
if (categoria_contribuyente != ""):
  lista_df_mono = pd.read_html("https://www.afip.gob.ar/monotributo/categorias.asp")
  categorias = lista_df_mono[0]
  for index, row in categorias.iterrows():
      marca = float(row[1].replace("$ ", "").replace(".", "").replace(",", "."))
      cate = row[0]
      fig.add_hline(marca,
                    line_dash="dash",
                    line_color=("red" if cate==categoria_contribuyente else "green"),
                    line_width=2,
                    label=dict(
                      text=cate,
                      textposition="end",
                      yanchor="top")
      )

# Le doy un "toque estético" final a la Figure con los dos plots (total y acumulado)
fig.update_layout(
   yaxis=dict(
    ),
    xaxis=dict(
      showgrid=True,
      showticklabels=True
    ),
    yaxis_tickformat='0,'
)
st.plotly_chart(fig)
