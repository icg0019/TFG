from .usuario import User
import pyodbc

#Parámetros de conexion
server = 'FNSVSQL05'
database = 'PEDIDOS_TETRA_DB'
username = 'sa'
password = 'FNSVSQL05'

# Crea la cadena de conexión
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

class ModelUser():

    @classmethod
    def login(self, user):
      try:
        # Intenta establecer la conexión
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users_Flask WHERE Usuario = ?", user.usuario)
        rows = cursor.fetchall()
        # Cierra la conexión
        connection.close()
        if len(rows)!=0:
          for row in rows: 
            passd=user.password
            print(f"ROW{row[1]}    y    {user.password}")
            coincide_password=User.check_password(row[1], user.password)
            if(coincide_password): 
              user=User(row[0],row[1])
              return user
            else: 
              return False
        else:
          return None
      except pyodbc.Error as ex:
        # Si hay un error, imprime el mensaje de error
        print("Error al intentar conectar a la base de datos:", ex)
        raise Exception(ex)
      
    @classmethod
    def get_by_id(self,user):
      try:
          connection = pyodbc.connect(connection_string)
          cursor = connection.cursor()
          cursor.execute("SELECT * FROM Users_Flask WHERE Usuario = ?", user)
          rows = cursor.fetchall()
          # Cierra la conexión
          connection.close()
          if len(rows)!= 0:
              for row in rows: 
                return User(row[0], row[1])
          else:
              return None
      except Exception as ex:
          raise Exception(ex)
          #return "No hay conexion a la base de datos"