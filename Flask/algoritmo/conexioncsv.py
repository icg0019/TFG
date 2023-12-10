import pandas as pd
import os

class ConexionCSV:
    def __init__(self, ruta):
        self.csv = ruta
        self.df_datos=self.obtener_datos()

    def obtener_datos(self):
        try:
            # Cargar datos desde el archivo CSV
            df = pd.read_csv(self.csv)
            return df
        except FileNotFoundError:
            print(f"El archivo CSV en la ruta '{self.csv}' no se encontró.")
            return None
        except pd.errors.EmptyDataError:
            print(f"El archivo CSV en la ruta '{self.csv}' está vacío.")
            return None
        except pd.errors.ParserError as e:
            print(f"Error al analizar el archivo CSV en la ruta '{self.csv}': {e}")
            return None
    
    #Funcion para coger el df de la ruta del csv
    def get_datos(self):
      return self.df_datos

if __name__ == "__main__":
    # Instancia de la clase para un archivo CSV específico
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(carpeta_actual, 'Necesidades_origenes', 'edge.csv')
    conexion_csv = ConexionCSV(ruta)
    # Utilizar la instancia para obtener datos
    datos_csv = conexion_csv.obtener_datos()
    if datos_csv is not None:
        print(datos_csv)