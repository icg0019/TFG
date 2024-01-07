import pandas as pd



class Pedido:
    def __init__(self, productos, tramos_df, registro):
        self.pedido = []
        self.tramos = 1
        self.tramos_superados = [0,0,0,0,0]
        self.pistas = 5
        self.productos = productos
        self.tramos_df = tramos_df
        self.registro=registro

    #Funcion para iniciar un pedido
    def iniciar_pedido(self,productos_a_revisar):
        self.registro.registrar(f"Vamos a inicializar el pedido con el primer producto {self.productos.sacar_indice_producto(0)}")
        producto=self.productos.sacar_indice_producto(0)#Iniciamos el primer producto que tiene que quedar cubierto
        self.pedido.append(producto) #añadimos el primer producto al pedido
        self.tramos_df.loc[producto, "Apariciones"] =  1 #actualizamos las apariciones de ese producto
        self.tramos_df["Apariciones"] = self.tramos_df["Apariciones"].fillna(0)
        num_productos=1
        
        #calculamos el df de los productos compatibles y lo ordenamos
        df_tramos_compatibles=pd.DataFrame(self.tramos_df.loc[self.tramos_df['Tramos_minimos'] != 0, ['Tramos_minimos', 'Tramos_maximos']])
        df_tramos_compatibles=df_tramos_compatibles.sort_values(by=['Tramos_minimos', "Tramos_maximos"], ascending=[True, True])
        self.registro.registrar(f"Estas son las necesidades compatibles con el primer producto ordenadas por prioridad")
        self.registro.registrar(f"{self.tramos_df}")
       
        
        #ponemos los productos que se puedan
        for indice, fila in df_tramos_compatibles.iterrows():
            if (producto!=indice):
                self.pedido.append(indice)
                self.tramos_df.loc[indice, "Apariciones"] =  1
                num_productos+=1
         
            if (num_productos>=productos_a_revisar or len(self.pedido)>=self.pistas):
                break

    #Funcion para añadir productos repetidos que cumplan los tramos del pedido
    def anadir_productos_repetidos(self, productos_a_revisar):
        revision=1
        
        while len(self.pedido)<self.pistas and revision!=0:
            posible=0
            revision=0
            #Damos una vuelta por los productos a revisar y si se puede añadir se añade.
            while len(self.pedido)<5 and posible<productos_a_revisar: 

                if (self.tramos_df['Apariciones'].loc[self.pedido[posible]]+1)*self.tramos<=float(self.tramos_df['Tramos_maximos'].loc[self.pedido[posible]]):
                    self.pedido.append(self.pedido[posible])
                    self.tramos_df.loc[self.pedido[posible], "Apariciones"]+=1
                    revision+=1
                posible+=1

    #Funcion para añadir los productos compatibles cuyos tramos mínimos están cubiertos
    def anadir_prod_no_necesarios(self, producto_a_empezar):
        posible=producto_a_empezar
        
        while(len(self.pedido)<self.pistas):
            self.pedido.append(self.tramos_df.index[int(posible)]) #coge el indice
            self.tramos_df.loc[self.tramos_df.index[int(posible)], "Apariciones"]+=1 #Hacer ejemplos
            posible+=1
            if (posible>len(self.tramos_df)-1):
                posible=producto_a_empezar


    #Funcion que crear un pedido.
    def crearPedido(self, no_satisfechos,inicio):
        self.iniciar_pedido(no_satisfechos) #iniciamos el pedido
        self.registro.registrar(f"Pedido Inicial {self.pedido}")
        
        if (len(self.pedido)!=5):
            self.anadir_productos_repetidos(no_satisfechos) #añadimos productos repetidos que tengan necesidades mínimas
            self.registro.registrar(f"Pedido productos repetidos {self.pedido}")
            if (len(self.pedido)!=5): 
                self.anadir_prod_no_necesarios(inicio) #añadimos productos que los tramos mínimos están superados
                self.registro.registrar(f"Pedido superando tramos minimos: {self.pedido}")
        
        self.registro.registrar("Las apariciones serían las siguientes: ")
        self.registro.registrar(f"{self.tramos_df}")
 
        #una vez tenemos completado el pedido intentamos ir aumentando los tramos hasta que no se pueda
        self.aumentarTramos(self.tramos_df)


    #Funcion para ir aumentando los tramos
    def aumentarTramos(self,tramos_df):
        #tramos_df["Apariciones"] = tramos_df["Apariciones"].fillna(0) #rellenamos los valores a Nan con 0 para poder operar correctamente
        while True:
            self.tramos+=1
            aumentar_tramo = (float(self.tramos) * tramos_df["Apariciones"].astype(float) <= tramos_df['Tramos_maximos'].astype(float)).all() #comprobamos que se pueda aumentar los tramos

            if aumentar_tramo == False:
                self.registro.registrar(f"Intento aumentar tramos a {self.tramos} pero no lo consigo porque hay elementos que me lo impiden. Por tanto, me quedo con {self.tramos-1} tramos.")
                break
            else: 
                self.registro.registrar(f"Intento aumentar tramos a {self.tramos} y lo consigo.")
        self.tramos-=1


    #Funcion que intenta cambiar los productos para aumentar los tramos del pedido
    def mejorarPedido_tramos(self):
        pedido_temporal=self.pedido.copy()
        tramos_df_temporal=self.tramos_df.copy()
        primer_elemento=self.pedido[0] #nos quedamos con el primer elemento
        #buscamos el elemento/elementos cuyo valor de tramos maximos sea tramos
     
        productos_a_cambiar1=self.tramos_df[self.tramos_df['Tramos_maximos']<(self.tramos+1)*self.tramos_df['Apariciones']] #se hace una lista con los productos que están impidiendo hacer el cambio.
        productos_a_cambiar=productos_a_cambiar1.index.tolist()
        #Nos quedamos solo con los que estén en el pedido
        productos_a_cambiar = list(set(self.pedido) & set(productos_a_cambiar))
       
        self.registro.registrar(f"Se puede intentar cambiar los productos que tiene el pedido,  ya que tiene {productos_a_cambiar} productos que bloquean el aumento de tramos.")
    
        #Por cada posible cambio, vemos por que elemento podemos cambiar. si se puede cambiar, se hace el cambio
        cambios=0
        for i in productos_a_cambiar:
            for indice, fila in tramos_df_temporal.iterrows():
                self.registro.registrar(f"Producto {i} se intenta sustituir por producto {indice}")
                
                tramos_maximos=self.productos.get_tramos_maximos(indice)
                if ( indice not in productos_a_cambiar and float(tramos_maximos)>=(self.tramos+1)*(float(tramos_df_temporal.loc[indice, "Apariciones"])+1)):

                    
                    tramos_df_temporal.loc[i, "Apariciones"]-=1
                    indice_pedido=pedido_temporal.index(i)
                    pedido_temporal[indice_pedido]=indice
                    tramos_df_temporal.loc[indice, "Apariciones"]+=1
                    cambios+=1
                    self.registro.registrar(f"He hecho un cambio de producto {i} por {indice}")

                    break

 
        if cambios==len(productos_a_cambiar):
            self.registro.registrar(f"He conseguido cambiar estos productos {productos_a_cambiar} que bloqueaban el aumento de tramos. El nuevo pedido es {pedido_temporal} y las apariciones modificadas son:")
            self.registro.registrar(f"{tramos_df_temporal}")
            

            #Comprobamos que el primer elemento sea el mismo que antes, si no es asi, se mueve al primer lugar para seguirle teniendo de referencia, ya que es el que queremos completar.
            if (primer_elemento!=pedido_temporal[0]):
                pedido_temporal.insert(0,pedido_temporal.pop(pedido_temporal.index(primer_elemento)))
            return pedido_temporal, tramos_df_temporal
        self.registro.registrar(f"No he conseguido cambiar todos los productos que bloqueaban el aumento de tramos{productos_a_cambiar}")

        return self.pedido, self.tramos_df
    
    #Funcion para mejorar el pedido en pedido que tiene mas de 5 compatibilidades
    def mejorarpedido(self): 
        #Si el maximo del primer elemento es igual a tramos, los tramos minimos no se pueden mejorar.
        tramos_maximos_0=self.productos.get_tramos_maximos(self.pedido[0])
        if (float(tramos_maximos_0)<=self.tramos):
            self.registro.registrar(f"El primer elemento ya no puede aumentar tramos, por lo que ya tenemos el pedido optimo.")
    
        #si no, intentamos quitar el elemento del pedido que nos esta bloqueando y sustituirlo por otro con un numero de tramos máximos mayor.
        else:
            lista_pedido_tramos_df=self.mejorarPedido_tramos()
            pedido_temporal=lista_pedido_tramos_df[0]
            tramos_df_temporal=lista_pedido_tramos_df[1]

            if (self.pedido!=pedido_temporal): #Si he conseguido cambiar los productos del pedido
                self.pedido=pedido_temporal #cambio el pedido
                self.tramos_df=tramos_df_temporal #cambio el tramos_df

                
                self.aumentarTramos(self.tramos_df) #intento aumentar tramos
                #breakpoint()
      
        self.pedido.append(self.tramos)

        return self.pedido, self.tramos_df

    #Funcion para ir mejorandoPedidos en bucle hasta que no se pueda mas
    def mejorarHastaOptima(self): 
        cambio_pedido=True
        pedido_original=self.pedido.copy()
        while cambio_pedido is True: 
            pedido_tramos_df=self.mejorarpedido() #intentamos mejorar el pedido
            self.pedido=pedido_tramos_df[0]
            self.tramos_df=pedido_tramos_df[1]
            if (self.pedido==pedido_original):
                self.pedido.pop(-1)
                cambio_pedido=False
            else: 
                pedido_original=self.pedido.copy()
                self.tramos=self.pedido[-1]
                self.pedido.pop(-1)
      
        self.registro.registrar(f"PEDIDO OPTIMO {self.pedido} y los tramos {self.tramos}")
        
        
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
        self.registro.registrar(f"Pedido {self.pedido} con tramos {self.tramos}")
    
    #Funcion que calcula la penalizacion del pedido
    def calcular_penalizacion(self):
        if (self.tramos<5):
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
    
    
    #Funcion para registrar los valores iniciales del pedido
    def explicar_inicio(self): 
        self.registro.registrar(f"HACEMOS UN PEDIDO, LOS VALORES INICIALES SON LOS SIGUIENTES:")
        self.registro.registrar(f"Productos")
        self.registro.registrar(f"{ self.productos.get_productos()}")
        self.registro.registrar("Compatibilidades")
        self.registro.registrar(f"{self.productos.get_compatibilidades()}")
        