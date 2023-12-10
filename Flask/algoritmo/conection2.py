import pyodbc
import pandas as pd
import os 

server = '5woh4oqmiv5uxeqcse3f5fwoim-hrnx4eismtnudhdnfhjknac4yi.datawarehouse.pbidedicated.windows.net'
database = 'PEDIDOS_TETRA'
username = 'irene.cuadrado@grupofrias.es'
password = ''  # Mi Contraseña
table = 'Necesidades_briks_SLIM'
auth = 'ActiveDirectoryPassword'

#Funcion para obtener la contraseña, la definimos en una variable de entorno para no meterla por código
def obtener_contraseña():
    # Hay que definir la variable de entorno AD_PASSWORD
    return os.environ.get('PASSWORD')

def crearconexion(nombre_tabla):
  table=nombre_tabla
  #Crear dataframe
  df = pd.DataFrame(columns=["MATNR", "REFERENCIA", "C1", "C2", "Necesidades_min", "Necesidades_max"])
  try:
    # Crear conexión 
    #password = obtener_contraseña()
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server +
                          ';DATABASE=' + database + ';Authentication=' + auth +
                          ';UID=' + username + ';PWD=' + password + ';ENCRYPT=yes')
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM " + table)
    row = cursor.fetchone()

    # Crear dataframe y rellenarlo. 
    #df = pd.DataFrame(columns=["MATNR", "REFERENCIA", "C1", "C2", "Necesidades_min", "Necesidades_max"])
    while row:        
        nueva_fila1 = {"MATNR": row[0], "REFERENCIA": row[1], "C1": row[2],"C2": row[3],"Necesidades_min": row[4], "Necesidades_max": row[5]}
        df = pd.concat([df, pd.DataFrame(nueva_fila1, index=[0])], ignore_index=True)
        row = cursor.fetchone()
  except pyodbc.Error as e:
        print("Error de conexión:", e)
        return None
  finally: 
    try: 
      # Cerrar conexión
      cnxn.close()
    except: 
      pass
  #df.to_csv('500.csv', index=False)
  return df


def crearconexionPedidos(nombre_tabla):
  table=nombre_tabla
  #Crear dataframe
  df = pd.DataFrame(columns=["Pedido", "posicion", "material", "cantidad", "Fecha"])
  try:
    # Crear conexión 
    #password = obtener_contraseña()
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server +
                          ';DATABASE=' + database + ';Authentication=' + auth +
                          ';UID=' + username + ';PWD=' + password + ';ENCRYPT=yes')
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM " + table)
    row = cursor.fetchone()

    # Crear dataframe y rellenarlo. 
    #df = pd.DataFrame(columns=["MATNR", "REFERENCIA", "C1", "C2", "Necesidades_min", "Necesidades_max"])
    while row:        
        nueva_fila1 = {"Pedido": row[0], "posicion": row[1], "material": str(row[2]),"cantidad": row[3],"Fecha": row[4]}
        df = pd.concat([df, pd.DataFrame(nueva_fila1, index=[0])], ignore_index=True)
        row = cursor.fetchone()
  except pyodbc.Error as e:
        print("Error de conexión:", e)
        return None
  finally: 
    try: 
      # Cerrar conexión
      cnxn.close()
    except: 
      pass
  
  df.to_csv('Historico_Pedidos.csv', index=False)
  return df


if __name__ == "__main__":
  #df=crearconexion('Necesidades_briks_SLIM')
  df=crearconexionPedidos("PEDIDOS_BRIKS")