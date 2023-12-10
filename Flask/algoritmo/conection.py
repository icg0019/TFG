import pyodbc
import pandas as pd


server = '5woh4oqmiv5uxeqcse3f5fwoim-hrnx4eismtnudhdnfhjknac4yi.datawarehouse.pbidedicated.windows.net'
database = 'PEDIDOS_TETRA'
username = 'irene.cuadrado@grupofrias.es'
table = 'Necesidades_briks_SLIM'
auth = 'ActiveDirectoryInteractive'

def crearconexion():
  #Crear conexion 
  cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';Authentication='+auth+';UID='+username+';ENCRYPT=yes')
  cursor = cnxn.cursor()
  cursor.execute("SELECT * FROM "+table)
  row = cursor.fetchone()

  #Crear dataframe y rellenarlo. 
  df = pd.DataFrame(columns=["MATNR", "REFERENCIA", "C1","C2", "Necesidades_min", "Necesidades_max"])
  while row:
    nueva_fila1 = {"MATNR": row[0], "REFERENCIA": row[1], "C1": row[2],"C2": row[3],"Necesidades_min": row[4], "Necesidades_max": row[5]}
    df = pd.concat([df, pd.DataFrame(nueva_fila1, index=[0])], ignore_index=True)
    row = cursor.fetchone()
  #print(df)
  #Cerrar conexion
  cnxn.close()
  return df
