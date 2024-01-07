import pandas as pd
import math

class Necesidades:
    def __init__(self, df):
        self.productos = self.crear_conjunto_productos(df)
        self.compatibilidades=self.compatibilidad_productos_df()
        self.anadirsatisfecho()  #Añadimos la columna de insatisfecho
        self.anadircompatibilidades() #Añadimos una columna con el numero de compatibilidades que tiene cada producto
        self.actualizarSatifecho()#Actualizamos la columna de satisfecho
        self.ordenarProductos()  #Ordenamos los productos en funcion del numero de compatibilidades
    

    #Funcion para crear el conjunto de productos, modificando las necesidades por tramos
    def crear_conjunto_productos(self,df): 
      df['Necesidades_max'] = (df['Necesidades_max'] / 17200).apply(lambda x: math.ceil(x))
      df['Necesidades_min'] = (df['Necesidades_min'] / 17200).apply(lambda x: math.ceil(x))
      df.rename(columns={'Necesidades_max': 'Tramos_maximos'}, inplace=True)
      df.rename(columns={'Necesidades_min': 'Tramos_minimos'}, inplace=True)
      return df
    
    #Funcion para añadir la columna Satisfecho inicializada a 0
    def anadirsatisfecho(self): 
      self.productos['Satisfecho'] = 0
      
    #Funcion para contar las compatibilidades 
    def anadircompatibilidades(self): 
      self.productos["Compatibilidad"]=self.compatibilidades.sum(axis=1)
      
    #Funcion para actualizar el estado de satisfecho
    def actualizarSatifecho(self): 
      self.productos.loc[self.productos['Tramos_minimos'] == 0, 'Satisfecho'] = 1
      
    #Funcion para ordenar los productos
    def ordenarProductos(self): 
      self.productos.sort_values(by=['Satisfecho','Compatibilidad'], inplace=True, ascending=[True, True]) 
           
    #Función que devuelve una matriz binaria con los productos. Si el producto i puede ir con el producto j, 1, si no 0
    def compatibilidad_productos_df(self):
      tamano = len(self.productos)
      matriz_df = pd.DataFrame(0, index=range(tamano), columns=range(tamano)) 
      for i in range(tamano):
        for j in range(i, tamano):
            colores = set([self.productos.at[i, 'C1'], self.productos.at[i, 'C2'], self.productos.at[j, 'C1'], self.productos.at[j, 'C2']])
            colores = {elemento for elemento in colores if not pd.isna(elemento)} #si lo traemos desde csv, lo coge como nan los vacios, por lo que incluimos esto
            if len(colores) <= 2:
               matriz_df.at[i, j] = 1
               matriz_df.at[j, i] = 1
            else:
              matriz_df.at[i, j] = 0
              matriz_df.at[j, i] = 0
      return matriz_df
    
      
    #Funcion para calcular un df con los productos compatibles del elemento escogido
    def calcular_prod_compatibles(self,indice):
      indice_primera_fila = self.productos.index[indice] #nos da el indice de producto pasado
      #Ver los productos que son compatibles con ese material 
      productos_compatibles_df= self.compatibilidades.iloc[indice_primera_fila] #nos da la fila de ese indice.
      productos_compatibles_df = productos_compatibles_df[productos_compatibles_df == 1].index #saca los indices de los productos compatibles
      return productos_compatibles_df
    
    #Funcion para calcular si queda algun producto insatisfecho
    def es_satisfecho(self): 
      insatisfechos = (self.productos['Satisfecho'] == 0).sum()
      if insatisfechos==0:
        return True
      return False
    
    # Funcion para extraer la columna 'Tramos' usando los índices de interés. Se dejan los productos cuyos tramos_maximos sean igual a cero al final y el resto se ordena de manera descencente por tramos mínimos
    def extraer_tramos_compatibles(self, productos_compatibles_df): 
      tramos_df=pd.DataFrame(self.productos.loc[productos_compatibles_df, ['Tramos_minimos','Tramos_maximos']]).sort_values(by='Tramos_minimos', ascending=False)
      tramos_df['es_cero'] = tramos_df['Tramos_maximos'] == 0 # Crear una columna auxiliar para indicar si el valor es cero
      tramos_df=tramos_df.sort_values(by='es_cero', ascending=True) #ordenamos para dejar abajo los que los tramos máximos estén completos
      tramos_df = tramos_df.drop('es_cero', axis=1) #Se borra la columna auxiliar
      return tramos_df
    
    
    #Funcion para extraer los tramos minimos no satisfechos
    def extraer_tramos_no_satisfechos(self,tramos_df): 
      tramos_minimos_no_satisfecho = pd.DataFrame(tramos_df.loc[tramos_df['Tramos_minimos'] != 0, ['Tramos_minimos', 'Tramos_maximos']])
      return tramos_minimos_no_satisfecho
    
    #Funcion para sacar los tramos maximos del elemento x
    def get_tramos_minimos(self, x): 
      return self.productos.loc[x, "Tramos_minimos"]
    
    #Funcion para modificar los tramos_maximos del elemeto x
    def set_tramos_minimos(self, x, tramos): 
      self.productos.loc[x, "Tramos_minimos"]=tramos
    
    #Funcion para sacar los tramos maximos del elemento x
    def get_tramos_maximos(self, x): 
      return self.productos.loc[x, "Tramos_maximos"]
    
    #Funcion para modificar los tramos_maximos del elemeto x
    def set_tramos_maximos(self, x, tramos): 
      self.productos.loc[x, "Tramos_maximos"]=tramos
        
    #Funcion para actualizar los tramos maximos y minimos de productos
    def actualizar_tramos(self,pedido, tramos):
      for i in pedido: 
        if self.productos.loc[i, "Tramos_minimos"]-tramos<0:
            self.productos.loc[i, "Tramos_minimos"]=0
        else: 
          self.productos.loc[i, "Tramos_minimos"]-=tramos
        if self.productos.loc[i, "Tramos_maximos"]-tramos<0:
          self.productos.loc[i, "Tramos_maximos"]=0
          
        else: 
          self.productos.loc[i, "Tramos_maximos"]-=tramos
    
    #Funcion para sacar el producto que este en el indice  
    def sacar_indice_producto(self,indice): 
      return self.productos.index[indice]
    
    #Funcion para sacar el matnr del indice 
    def get_matnr(self, indice): 
      return self.productos.loc[indice, "MATNR"]
    
    #Funcion para sacar la referencia del producto del indice 
    def get_referencia(self, indice): 
      return self.productos.loc[indice, "Referencia"]
    
    #Funcion para coger los productos
    def get_productos(self): 
      return self.productos
    
    #Funcion para coger las compatibilidades
    def get_compatibilidades(self): 
      return self.compatibilidades
    
    
    