import pandas as pd

lista_df = pd.read_html("https://www.afip.gob.ar/monotributo/categorias.asp")

print(lista_df[0].columns.tolist())

print(lista_df[0])
