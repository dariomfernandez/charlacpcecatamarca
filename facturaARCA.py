import tabula

archivo = "20274025493_011_00003_00000386.pdf"

dfs = tabula.read_pdf(archivo, area=[250,14,250+226,14+562], pages="1")

print(dfs[0].columns.tolist())

print(dfs[0])
