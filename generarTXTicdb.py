import pandas as pd
import numpy as np

df = pd.read_excel("Compensaciones IDCB-Ganancias 2024.ods", engine="odf", skiprows=2)
#print(df)

cuit_titular = "20123456789"

df.drop('BANCO', axis=1, inplace=True)
#print(df)

df['CUIT TITULAR'] = cuit_titular
#print(df)

df['PERÍODO'] = pd.to_datetime(df['PERÍODO']).dt.strftime('%Y%m')
#print(df)

df['MONTO'] = (df['MONTO']* 100).astype(int).astype(str).str.zfill(16)
#print(df)

new_order = ['CUIT TITULAR', 'PERÍODO', 'CUIT BANCO', 'CBU', 'MONTO']
print(df[new_order])

df.to_csv("idcb.csv", sep=";", index=False, header=False)

np_array = df.to_numpy()
np.savetxt('idcb.txt', np_array, delimiter="", fmt='%s')
