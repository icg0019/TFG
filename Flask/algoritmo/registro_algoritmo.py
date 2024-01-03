import os

class Registro:
    def __init__(self, carpeta, nombre_archivo):
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        self.ruta_carpeta = os.path.join(carpeta_actual, 'Resultados', carpeta)
        self.ruta_archivo = os.path.join(self.ruta_carpeta, nombre_archivo)
        self.nombre_archivo = nombre_archivo

        if not os.path.exists(self.ruta_carpeta):
            os.makedirs(self.ruta_carpeta)

    def registrar(self, mensaje):
        with open(self.ruta_archivo, 'a') as archivo:
            archivo.write(f'\n{mensaje}\n')











