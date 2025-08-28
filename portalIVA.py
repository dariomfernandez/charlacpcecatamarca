import tabula
import fitz
import pdfplumber
import pypdf_table_extraction
import glob
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# Function que extrae la info del PDF del form 2083
def extraer_2083(pdf):
    global df
    ventas = tabula.read_pdf(pdf, area=[180,15,180+70,15+560], pages="1", silent=True)
    #print("VENTAS")
    #print(ventas[0].shape)
    compras = tabula.read_pdf(pdf, area=[320,15,320+70,15+560], pages="1", silent=True)
    #print("COMPRAS")
    #print(compras[0].shape)
    periodo = tabula.read_pdf(pdf, area=[102,175,102+18,175+225], pages="1", silent=True)
    #print("PERIODO")
    #print(dfs)
    #print(pdf)
    df.loc[len(df)] = [periodo[0].columns.tolist()[0][-6:], ventas[0].iloc[0, 3], ventas[0].iloc[1, 3], compras[0].iloc[0, 3], compras[0].iloc[1, 3], 0, 0, 0, 0, 0]

# Function que extrae la info del PDF del form 2002
def extraer_2002(pdf):
    global df
    bi = tabula.read_pdf(pdf, area=[175,36,175+365,36+524], pages="1", silent=True)
    dfBi = bi[0]
    #print(dfBi)
    stpa = dfBi.loc[dfBi['Concepto'] == 'Saldo Técnico a Favor del Responsable del Período anterior'].iloc[0, 1]
    stp = dfBi.loc[dfBi['Concepto'] == 'Saldo Técnico a Favor del Responsable del Período'].iloc[0, 1]
    starca = dfBi.loc[dfBi['Concepto'] == 'Saldo técnico a favor de ARCA'].iloc[0, 1]
    retper = dfBi.loc[dfBi['Concepto'] == 'Total de retenciones, percepciones y pagos a cuenta computables en el período neto de restituciones'].iloc[0, 1]
    apagar = dfBi.loc[dfBi['Concepto'] == 'Saldo del Impuesto a Favor de ARCA'].iloc[0, 1]
    periodo = tabula.read_pdf(pdf, area=[92,130,92+28,130+230], pages="1", silent=True)
    per = periodo[0].columns.tolist()[0][-6:]
    df.loc[df['Período'] == per, 'STPA'] = stpa
    df.loc[df['Período'] == per, 'ST del período'] = stp
    df.loc[df['Período'] == per, 'ST favor ARCA'] = starca
    df.loc[df['Período'] == per, 'Ret/Per'] = retper
    df.loc[df['Período'] == per, 'A pagar'] = apagar

df = pd.DataFrame(columns=['Período', 'DF', 'Rest DF', 'CF', 'Rest CF', 'STPA', 'ST del período', 'ST favor ARCA', 'Ret/Per', 'A pagar'])

# Listo los archivos de la carpeta, que coincidan con el patrón "*2083*"
for archivo in glob.glob("*2083*.pdf"):
    # Lo mando a procesar
    pass
    #print(f"ARCHIVO: {archivo}")
    extraer_2083(archivo)

for archivo in glob.glob("*DJF2002*.pdf"):
    # Lo mando a procesar
    pass
    #print(f"ARCHIVO: {archivo}")
    extraer_2002(archivo)

print(df)

df.sort_values(by='Período').to_excel("IVA.xlsx")
