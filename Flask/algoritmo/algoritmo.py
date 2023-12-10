import pandas as pd
from decimal import Decimal
import numpy as np
from datetime import datetime
import os
#import conection

try:
    from necesidades import Necesidades
    from conexioncsv import ConexionCSV
    from pedido import Pedido
    from conection2 import crearconexion
except ImportError:
    # Si falla la importación, intentar importar desde la ruta del módulo
    from .necesidades import Necesidades
    from .conexioncsv import ConexionCSV
    from .pedido import Pedido
    from .conection2 import crearconexion


#Version 10 - se optimiza el tema de las mejoras de pedidos. Lo que se hace es dejar a optima las mejoras de aumentos de tramos de pedidos. Solo Queda optimizacion cuando no se puede aumentar los tramos, ver si se pueden reducir los 

#Funcion datos de inicio
def ConjuntoPedido(csv): 
  carpeta_actual = os.path.dirname(os.path.abspath(__file__))
  ruta = os.path.join(carpeta_actual, 'Necesidades_origenes', 'edge.csv')
  df_productos=ConexionCSV(ruta).obtener_datos()
  return df_productos


#Funcion que exportar los datos en formato solicitado a un csv
def exportar_a_csv(pedidos):
    filas = []
    for pedido in pedidos:
        fila = pedido.devolver_pedido_por_matnr()
        fila.append(pedido.devolver_cantidad())
        filas.append(fila)
        
    df_csv = pd.DataFrame(filas, columns=['Producto 1', 'Producto 2', 'Producto 3', 'Producto 4', 'Producto 5','Cantidad'])
        
    ahora=datetime.now()
    timestamp = ahora.strftime('%Y%m%d_%H%M%S') 
    nombre_archivo = f'pedidos{timestamp}.csv' 
    df_csv.to_csv(nombre_archivo, index=False)
    
#Funcion que exportar los datos en formato solicitado a un csv
def df_a_exportar(pedidos):
  filas = []
  for pedido in pedidos:
      fila = pedido.devolver_pedido_por_matnr()
      fila.append(pedido.devolver_cantidad())
      filas.append(fila)
        
  df_csv = pd.DataFrame(filas, columns=['Producto 1', 'Producto 2', 'Producto 3', 'Producto 4', 'Producto 5','Cantidad'])
  return df_csv

#Funcion que calcula la penalizacion por brik
def penalizacion_por_brik(pedidos): 
  briks=0
  penalizacion=0
  for pedido in pedidos: 
    penalizacion+=pedido.calcular_penalizacion()
    briks+=pedido.devolver_cantidad()
  return penalizacion/briks
  
  
#Funcion que calcula los pedidos de la forma más optima posible
def optimizacion(df): 
  grupo_pedidos= []
  productos=Necesidades(df)
  #df=conection2.crearconexion()
  productos.imprimir_compatibilidad()
  productos.imprimir_productos()
  insatisfecho = productos.es_satisfecho()
  #cpoint()
  print(f"Insatisfechos {insatisfecho}")
  while insatisfecho==False:
    #calculamos los productos compatibles del productos elegido. En este caso siempre eligmos el primero
    productos_compatibles_df = productos.calcular_prod_compatibles(0)
    print(f"Productos compatibles {productos_compatibles_df}")
    productos_compatibles=len(productos_compatibles_df)  #comprobamos cuantos productos compatibles hay
    print(f"Productos compatibles {productos_compatibles}")
    
    # Extraer la columna 'Tramos' usando los índices de interés
    tramos_df=productos.extraer_tramos_compatibles(productos_compatibles_df)
    print(f"Tramos completos en un mismo df {tramos_df}")
    #calculamos los productos compatibles no satisfechos 
    tramos_minimos_no_satisfecho = productos.extraer_tramos_no_satisfechos(tramos_df)
    productos_compatibles_no_satisfechos=len(tramos_minimos_no_satisfecho)
    print(f"Tramos no satisfechos {tramos_minimos_no_satisfecho}")

    pedido=Pedido(productos, tramos_df)
    #Si tiene menos productos compatibles que 5 
    #breakpoint()
    if(productos_compatibles<5):
      no_satisfechos=productos_compatibles_no_satisfechos
      inicio=0
    else: 
      #si los productos no satisfechos son menores que 5, intentamos cubrir las pistas con los productos no satisfechos
      if(productos_compatibles_no_satisfechos<5):       
        #Inicializamos pedido
        no_satisfechos=productos_compatibles_no_satisfechos
        inicio=productos_compatibles_no_satisfechos
        
      else: 
        no_satisfechos=5
        inicio=5
        
    pedido.crearPedido(no_satisfechos,inicio) #creamos el pedido 
    pedido.mejorarHastaOptima() #mejoramos el pedido todo lo que podamos
    grupo_pedidos.append(pedido) #Actualizamos el pedido y lo añadimos al conjutno de pedidos
    
    #productos.actualizar_tramos(pedido.devolver_pedido(), pedido.devolver_tramos())  #Actualizamos los tramos de producto 
    
    #Actualizamos los tramos de los productos y añadimos penalizaciones en pedido si supera tramos maximos
    for i in pedido.devolver_pedido(): 
      if productos.get_tramos_minimos(i)-pedido.devolver_tramos()<0: 
        productos.set_tramos_minimos(i,0)
      else: 
        productos.set_tramos_minimos(i,productos.get_tramos_minimos(i)-pedido.devolver_tramos())
        
      if productos.get_tramos_maximos(i)-pedido.devolver_tramos()<0: 
        productos.set_tramos_maximos(i,0)
        pedido.supera_tramos_maximos(i,productos.get_tramos_maximos(i)-pedido.devolver_tramos())
      else: 
        productos.set_tramos_maximos(i,productos.get_tramos_maximos(i)-pedido.devolver_tramos())
    #breakpoint()
    
    productos.actualizarSatifecho()  #Actualizamos Satisfecho
    productos.ordenarProductos()  #Ordenamos productos
    productos.imprimir_compatibilidad()
    productos.imprimir_productos()
    pedido.imprimir_pedido()
    
    insatisfecho = productos.es_satisfecho()
    #breakpoint()
  #exportar_a_csv(grupo_pedidos) #exportamos los pedidos
  return grupo_pedidos
  
#Funcion inicial
if __name__ == "__main__":
  #Datos de entrada con los que trabajar. 
  #df=conection2.crearconexion()
  df=ConjuntoPedido('edge.csv')
  grupo_pedidos=optimizacion(df) #calculos los pedidos
  print(grupo_pedidos)
  for pedido in grupo_pedidos: 
    print(pedido.imprimir_pedido())
  exportar_a_csv(grupo_pedidos) #exportamos los pedidos
 