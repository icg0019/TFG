import pandas as pd
#import conjuntoproductos

class Pedido:
    def __init__(self, productos, tramos_df):
        self.pedido = []
        self.tramos = 1
        self.tramos_superados = [0,0,0,0,0]
        self.pistas = 5 
        self.productos = productos
        self.tramos_df = tramos_df

    #Funcion para iniciar un pedido
    def iniciar_pedido(self,productos_a_revisar): 
        producto=self.productos.sacar_indice_producto(0)#Iniciamos el primer producto que tiene que quedar cubierto
        self.pedido.append(producto) #añadimos el primer producto al pedido
        self.tramos_df.loc[producto, "Apariciones"] =  1 #actualizamos las apariciones de ese producto
        print(f"Máximos inicializando en el primer producto {self.tramos_df}")
        num_productos=1
  
        #calculamos el df de los productos compatibles y lo ordenamos
        df_tramos_compatibles=pd.DataFrame(self.tramos_df.loc[self.tramos_df['Tramos_minimos'] != 0, ['Tramos_minimos', 'Tramos_maximos']])
        df_tramos_compatibles=df_tramos_compatibles.sort_values(by=['Tramos_minimos', "Tramos_maximos"], ascending=[True, True])
        print(f"Df nuevo de tramos compatibles ordenados{df_tramos_compatibles}")
        
        #ponemos los productos que se puedan 
        for indice, fila in df_tramos_compatibles.iterrows():
            if(producto!=indice): 
                self.pedido.append(indice)
                self.tramos_df.loc[indice, "Apariciones"] =  1
                num_productos+=1
            print(self.tramos_df)
            if(num_productos>=productos_a_revisar or len(self.pedido)>=self.pistas): 
                break

    #Funcion para añadir productos repetidos que cumplan los tramos del pedido
    def anadir_productos_repetidos(self, productos_a_revisar): 
        revision=1
        print(f"Pedido antes de añadir duplicados {self.pedido}")
        
        while len(self.pedido)<self.pistas and revision!=0: 
            posible=0
            revision=0
            #Damos una vuelta por los productos a revisar y si se puede añadir se añade. 
            while len(self.pedido)<5 and posible<productos_a_revisar: 
                print(f"Vamos a añadir al pedido {self.pedido} un posible elemento ")
                print(f"Estamos en el elemento {self.pedido[posible]} y vamos a ver si {(self.tramos_df['Apariciones'].loc[self.pedido[posible]]+1)*self.tramos} es <= {float(self.tramos_df['Tramos_maximos'].loc[self.pedido[posible]])}")
                
                if (self.tramos_df['Apariciones'].loc[self.pedido[posible]]+1)*self.tramos<=float(self.tramos_df['Tramos_maximos'].loc[self.pedido[posible]]):
                    self.pedido.append(self.pedido[posible])
                    self.tramos_df.loc[self.pedido[posible], "Apariciones"]+=1
                    revision+=1
                posible+=1
                
    #Funcion para añadir los productos compatibles cuyos tramos mínimos están cubiertos
    def anadir_prod_no_necesarios(self, producto_a_empezar): 
        posible=producto_a_empezar
        while(len(self.pedido)<self.pistas): 
            self.pedido.append(self.tramos_df.index[posible])
            print(f"DDDDDDDDDDDDDDDDDDDDDDDDDDD{self.tramos_df.at[self.tramos_df.index[posible], 'Apariciones']}")
            self.tramos_df.at[self.tramos_df.index[posible], "Apariciones"]+=1 #Hacer ejemplos
            posible+=1.
            if(posible>len(self.tramos_df)-1): 
                posible=producto_a_empezar


    #Funcion que crear un pedido.
    def crearPedido(self, no_satisfechos,inicio): 
        self.iniciar_pedido(no_satisfechos) #iniciamos el pedido
        print(f"Pedido Inicial {self.pedido}")
        print(f"Pedido Inicial {self.tramos_df}")
        self.anadir_productos_repetidos(no_satisfechos) #añadimos productos repetidos si se puede 
        print(f"Pedido productos repetidos {self.pedido}")
        print(f"Pedido productos repetidos {self.tramos_df}")
        self.anadir_prod_no_necesarios(inicio) #añadimos productos que los tramos mínimos están superados
        print(f"Pedido superando tramos {self.pedido}")
        print(f"Pedido productos repetidos {self.tramos_df}")
        #breakpoint()
        #una vez tenemos completado el pedido intentamos ir aumentando los tramos hasta que no se pueda
        self.aumentarTramos(self.tramos_df)
        print(f"Tramos del pedido {self.tramos}")

    #Funcion para ir aumentando los tramos
    def aumentarTramos(self,tramos_df): 
        tramos_df["Apariciones"] = tramos_df["Apariciones"].fillna(0) #rellenamos los valores a Nan con 0 para poder operar correctamente
        while True: 
            self.tramos+=1
            print(f"Intento aumnentar los tramos a {self.tramos}")
            print(f"TRAMOS {tramos_df}")
            aumentar_tramo = (float(self.tramos) * tramos_df["Apariciones"].astype(float) <= tramos_df['Tramos_maximos'].astype(float)).all() #comprobamos que se pueda aumentar los tramos
            print(f"Aumentar tramos {aumentar_tramo}")
            if aumentar_tramo==False:
                break
        self.tramos-=1

    #Funcion que intenta cambiar los productos para aumentar los tramos del pedido
    def mejorarPedido_tramos(self): 
        pedido_temporal=self.pedido.copy()
        tramos_df_temporal=self.tramos_df.copy()
        primer_elemento=self.pedido[0] #nos quedamos con el primer elemento
        #buscamos el elemento/elementos cuyo valor de tramos maximos sea tramos
        print(f"Tramos{self.tramos}")
        productos_a_cambiar1=self.tramos_df[self.tramos_df['Tramos_maximos']<(self.tramos+1)*self.tramos_df['Apariciones']] #se hace una lista con los productos que están impidiendo hacer el cambio.
        productos_a_cambiar=productos_a_cambiar1.index.tolist() 
        #Nos quedamos solo con los que estén en el pedido
        productos_a_cambiar = list(set(self.pedido) & set(productos_a_cambiar))
        print(f"Productos antes del set {productos_a_cambiar}")
        print(f"Se puede aumentar tramos, ya que tiene {productos_a_cambiar} productos a cambiar")
    
        #Por cada posible cambio, vemos por que elemento podemos cambiar. si se puede cambiar, se hace el cambio
        cambios=0
        for i in productos_a_cambiar:
            for indice, fila in tramos_df_temporal.iterrows(): 
                print(f"Producto {i} se intenta sustituir por producto {indice}")
                tramos_maximos=self.productos.get_tramos_maximos(indice)
                if( indice not in productos_a_cambiar and float(tramos_maximos)>=(self.tramos+1)*(float(tramos_df_temporal.loc[indice, "Apariciones"])+1)): 
                    print(f"Tramos_df temporal antes de cambiar el {tramos_df_temporal.loc[i, 'Apariciones']} por {i}")
                    tramos_df_temporal.loc[i, "Apariciones"]-=1
                    print(f"Tramos_df temporal despues de cambiar las apariciones {tramos_df_temporal.loc[i, 'Apariciones']} por {i}")
                    indice_pedido=pedido_temporal.index(i)
                    print(f"Indice temporal antes de cambiar el {pedido_temporal[indice_pedido]} por {indice_pedido}")
                    pedido_temporal[indice_pedido]=indice
                    print(f"Indice temporal antes de cambiar el {tramos_df_temporal}")
                    tramos_df_temporal.loc[indice, "Apariciones"]+=1
                    print(f"Indice temporal despues de cambiar el {tramos_df_temporal}")
                    cambios+=1
                    print(f"He hecho un cambio de producto {i} por {indice}")
                    break     
            print(f"Tramos modificado: {tramos_df_temporal}")
            print(f"Pedido modificado: {pedido_temporal}")
        #breakpoint()
 
        if cambios==len(productos_a_cambiar): 
            print(f"He conseguido cambiar los pedidos, productos a cambiar {productos_a_cambiar}")
            #breakpoint()
            #Comprobamos que el primer elemento sea el mismo que antes, si no es asi, se mueve al primer lugar para seguirle teniendo de referencia, ya que es el que queremos completar.
            if(primer_elemento!=pedido_temporal[0]): 
                pedido_temporal.insert(0,pedido_temporal.pop(pedido_temporal.index(primer_elemento)))
            return pedido_temporal, tramos_df_temporal
        print(f"No he conseguido cambiar los pedidos, productos a cambiar {productos_a_cambiar}")
        #breakpoint()
        return self.pedido, self.tramos_df
    
    #Funcion para mejorar el pedido en pedido que tiene mas de 5 compatibilidades
    def mejorarpedido(self): 
        print(f"Mejorar pedido {self.pedido} con tramos {self.tramos}")
        print(f"Mejorar pedido tramos_df {self.tramos_df}")
        
        #Si el maximo del primer elemento es igual a tramos, los tramos minimos no se pueden mejorar. Pero intentamos cambiar de los otros 4 elementos a uno que supere los tramos minimos, para poder pasarle a satisfecho
        tramos_maximos_0=self.productos.get_tramos_maximos(self.pedido[0])
        if(float(tramos_maximos_0)<=self.tramos):
            #revisamos el numero de apariciones del primer elemento. Si el numero de interacciones es mayor que uno, intentamos reducir el numero de apariciones y ver si podemos mejorar el pedido 
            if(float(self.tramos_df.loc[self.pedido[0], "Apariciones"])>1): 
                print(5)
                
            print("No se puede aumentar tramos, pero vamos a intentar aumentar el número de satisfechos")
    
        #si no, intentamos quitar el elemento del pedido que nos esta bloqueando y sustituirlo por otro con un numero de tramos máximos mayor.  
        else: 
            lista_pedido_tramos_df=self.mejorarPedido_tramos() 
            pedido_temporal=lista_pedido_tramos_df[0]
            tramos_df_temporal=lista_pedido_tramos_df[1]
            print(f"Pedido temporal {pedido_temporal} y pedido normal {self.pedido}")
            print(f"tramos_df_temporal: {tramos_df_temporal}")
            if(self.pedido!=pedido_temporal): #Si he conseguido cambiar los productos del pedido
                print("He entrado en diferente pedidos")
                self.pedido=pedido_temporal #cambio el pedido 
                self.tramos_df=tramos_df_temporal #cambio el tramos_df
                print(f"Df modificado final {self.tramos_df}")
                print(f"Pedido moficado {self.pedido}")
                self.aumentarTramos(self.tramos_df) #intento aumentar tramos
                print(f"Tramos {self.tramos}")
                #breakpoint()
      
        self.pedido.append(self.tramos)   
        print(f"Pedido tramos después del bucle{self.pedido}")
        return self.pedido, self.tramos_df

    #Funcion para ir mejorandoPedidos en bucle hasta que no se pueda mas 
    def mejorarHastaOptima(self): 
        cambio_pedido=True
        pedido_original=self.pedido.copy()
        tramos_original=self.tramos
        #pedido_original.append(self.tramos)
  
        while cambio_pedido==True: 
            pedido_tramos_df=self.mejorarpedido() #intentamos mejorar el pedido
            self.pedido=pedido_tramos_df[0]
            self.tramos_df=pedido_tramos_df[1]
            if(self.pedido==pedido_original): 
                self.pedido.pop(-1)
                cambio_pedido=False
            else: 
                pedido_original=self.pedido.copy()
                self.tramos=self.pedido[-1]
                self.pedido.pop(-1)
        print(f"Este es el `pedido Óptimo {self.pedido} y los tramos {self.tramos}")
        #breakpoint()
        
        
    #Funcion que devuelve los tramos 
    def devolver_cantidad(self): 
        return self.tramos*17200
    
    #Funcion que devuelve los tramos 
    def devolver_tramos(self): 
        return self.tramos
    
    #Funcion que devuelve el pedido
    def devolver_pedido(self): 
        return self.pedido
    
    #Funcion que devuelve el pedido con su material
    def devolver_pedido_por_matnr(self): 
        matnr=[]
        for producto in self.pedido: 
            matnr.append(self.productos.get_matnr(producto))
        return matnr
    
    #Funcion para devolver un producto de la posicion p
    def devolver_producto_de_pedido(self, posicion): 
        return self.pedido[posicion]
    
    #Funcion que imprime el pedido 
    def imprimir_pedido(self): 
        print(f"Pedido {self.pedido} con tramos {self.tramos}")
    
    #Funcion que calcula la penalizacion del pedido
    def calcular_penalizacion(self): 
        if(self.tramos<5): 
            return 750
        else: 
            return 0

    #Funcion para comprobar que haya un pedido que se haya pasado de los tramos máximos
    def supera_tramos_maximos(self, producto, tramos): 
        posicion_elemento = self.pedido.index(producto)
        self.tramos_superados+=tramos
        
    #Funcion que calcula las cantidades de cada pedido y devuelve un dicionario con ellas.
    def cantidad_por_producto(self):
        devolver={} #dicionario con clave MATNR : CANTIDAD
        apariciones_df = self.tramos_df[self.tramos_df["Apariciones"] != 0] #calcula los productos que aparecen
        print(apariciones_df)
        for indice, fila in apariciones_df.iterrows(): 
            cantidad=apariciones_df.loc[indice, "Apariciones"]*self.tramos*17200
            matnr = self.productos.get_matnr(indice)
            devolver[matnr] =  "{:,.0f}".format(cantidad).replace(",", ".")
        return devolver
            