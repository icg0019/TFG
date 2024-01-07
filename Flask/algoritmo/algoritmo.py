import pandas as pd
from datetime import datetime
import os


try:
    from necesidades import Necesidades
    from conexioncsv import ConexionCSV
    from pedido import Pedido
    from conection import crearconexion
    from registro_algoritmo import Registro
except ImportError:
    # Si falla la importación, intentar importar desde la ruta del módulo
    from .registro_algoritmo import Registro
    from .necesidades import Necesidades
    from .conexioncsv import ConexionCSV
    from .pedido import Pedido
    from .conection import crearconexion


#Funcion datos de inicio
def ConjuntoPedido(csv):
  carpeta_actual = os.path.dirname(os.path.abspath(__file__))
  ruta = os.path.join(carpeta_actual, 'Necesidades_origenes', csv)
  df_productos=ConexionCSV(ruta).obtener_datos()
  return df_productos

#Funcion que exportar los datos en formato solicitado a un csv
def pedidos_a_exportar(pedidos):
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
def optimizacion(df, tipobrik):
  nombre_carpeta=f"{tipobrik}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
  grupo_pedidos= []
  productos=Necesidades(df) #creamos las necesidades
 
  insatisfecho = productos.es_satisfecho()
  while not insatisfecho:
    #calculamos los productos compatibles del productos elegido. En este caso siempre eligmos el primero
    productos_compatibles_df = productos.calcular_prod_compatibles(0)
    productos_compatibles=len(productos_compatibles_df)  #comprobamos cuantos productos compatibles hay

    # Extraer la columna 'Tramos' usando los índices de interés
    tramos_df=productos.extraer_tramos_compatibles(productos_compatibles_df)

    #calculamos los productos compatibles no satisfechos
    tramos_minimos_no_satisfecho = productos.extraer_tramos_no_satisfechos(tramos_df)
    productos_compatibles_no_satisfechos=len(tramos_minimos_no_satisfecho)

    
    nombre_fichero=f"pedido{len(grupo_pedidos)+1}.txt"
    registro = Registro(nombre_carpeta,nombre_fichero)
    pedido=Pedido(productos, tramos_df, registro)
    pedido.explicar_inicio()
    
    #Si tiene menos productos compatibles que 5 
    if (productos_compatibles < 5):
      no_satisfechos=productos_compatibles_no_satisfechos
      inicio=0
    else:
        #si los productos no satisfechos son menores que 5, intentamos cubrir las pistas con los productos no satisfechos
      if (productos_compatibles_no_satisfechos<5):       
        #Inicializamos pedido
        no_satisfechos=productos_compatibles_no_satisfechos
        inicio=productos_compatibles_no_satisfechos
        
      else: 
        no_satisfechos=5
        inicio=5
        
    pedido.crearPedido(no_satisfechos,inicio) #creamos el pedido
    pedido.mejorarHastaOptima() #mejoramos el pedido todo lo que podamos
    grupo_pedidos.append(pedido) #Actualizamos el pedido y lo añadimos al conjutno de pedidos
    
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
    
    productos.actualizarSatifecho()  #Actualizamos Satisfecho
    productos.ordenarProductos()  #Ordenamos productos
    
    insatisfecho = productos.es_satisfecho()

    #registro.registrar(f"Se han satisfecho todas las necesidades minimas de los productos")
    #exportar_a_csv(grupo_pedidos) #exportamos los pedidos
  return grupo_pedidos
  
