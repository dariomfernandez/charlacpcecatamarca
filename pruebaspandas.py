import pandas as pd

df = pd.read_excel(
    io='master_ventas.xlsx',
    engine='openpyxl',
    #sheet_name='Table1',
    #skiprows=1,
    #usecols='A:Z',
)

#print(df.dtypes)

#print(df.shape)

df['fecha'] = pd.to_datetime(df['fecha'])
print(df.sort_values(by='fecha', ascending=False)['fecha'])
