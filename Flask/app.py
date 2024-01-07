from flask import Flask, render_template, url_for, request,send_file,redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from algoritmo.conexioncsv import ConexionCSV
from algoritmo.algoritmo import optimizacion, penalizacion_por_brik, pedidos_a_exportar
import os
import pandas as pd
from io import BytesIO
from config import config
import json
from werkzeug.exceptions import BadRequestKeyError
from models.models import ModelUser
from models.usuario import User
import logging
from datetime import datetime

app=Flask(__name__)
login_manager_app = LoginManager(app)
app.secret_key='LDfj/8adf'

@login_manager_app.user_loader
def load_user(user):
  return ModelUser.get_by_id(user)

#Función para obtener datos segun de que origen
def obtener_Datos(csv):
  carpeta_actual = os.path.dirname(os.path.abspath(__file__))
  ruta_csv = os.path.join(carpeta_actual, 'algoritmo','Necesidades_origenes', csv)
  df=ConexionCSV(ruta_csv).obtener_datos()
  return df

@app.route ('/')
def index():
  return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login ():
    #si ya han enviado los datos de login
  if (request.method=='POST'):
    user=User(request.form['username'], request.form['password']) #hacemos un usuario con el usuario y contraseña
    logged_user=ModelUser.login(user) #pasamos el usuari opara hacer las comprobacion de si está o no en la bd

    if (logged_user is not None):
      if (logged_user is not False):
        try:
          login_user(logged_user)
        except Exception as e:
          logging.error(f"Error: {e}")
        return redirect(url_for('inicio'))
      else:
        error = 'Contraseña incorrecta. Inténtalo de nuevo.'
      return render_template('auth/login.html', error = error)
    else:
      error = 'Usuario no encontrado. Inténtalo de nuevo.'
      return render_template('auth/login.html',error = error)
  else: 
    return render_template('auth/login.html')

@app.route ('/logout')
def logout():
  logout_user()
  return redirect(url_for('login'))


@app.route("/inicio")
@login_required
def inicio():
  return render_template('inicio.html')

@app.route("/Briks_edge")
@login_required
def briks_edge():
  df=obtener_Datos('edge.csv')
    #df=conection.crearconexion('Necesidades_briks_EDGE')
  
  df_mostrar = df.loc[~((df['Necesidades_max'] == 0) & (df['Necesidades_min'] == 0))] #para mostrar, quitamos las que no tienen ningun tipo de necesidad

  return render_template('briks.html', df=df, df_mostrar=df_mostrar, tipobrik="EDGE")


@app.route("/Briks_500")
@login_required
def brik_500():
  df=obtener_Datos('500.csv')
  #df=conection.crearconexion('Necesidades_briks_500')
  df_mostrar = df.loc[~((df['Necesidades_max'] == 0) & (df['Necesidades_min'] == 0))]#para mostrar, quitamos las que no tienen ningun tipo de necesidad
  return render_template('briks.html', df=df, df_mostrar=df_mostrar,tipobrik="500")

@app.route("/Briks_slim")
@login_required
def briks_slim():
  df=obtener_Datos('slim.csv')
  #df=conection.crearconexion('Necesidades_briks_SLIM')
  df_mostrar = df.loc[~((df['Necesidades_max'] == 0) & (df['Necesidades_min'] == 0))] #para mostrar, quitamos las que no tienen ningun tipo de necesidad
  
  return render_template('briks.html', df=df, df_mostrar=df_mostrar, tipobrik="SLIM")

@app.route('/generar_pedidos', methods=['GET','POST'])
@login_required
def generar_pedidos():
    #Si ponen la url directamente por el navegador
  if request.method == 'GET':
    return redirect(url_for('inicio'))
  df_json = request.form.get('df')# Recibo el DataFrame desde el formulario
  df = pd.read_json(df_json)
  tipobrik = request.form.get('tipobrik')
  pedidos = optimizacion(df, tipobrik) #genero los pedidos optimos
  penalizacion=round(penalizacion_por_brik(pedidos),4) #calculo la penalizacion

#Calculamos los pedidos por cantidades para mostrarselos al usuario
  pedidos_por_cantidades=[]
  for pedido in pedidos:
    pedidos_por_cantidades.append(pedido.cantidad_por_producto())
  pedidos_por_cantidades = sorted(pedidos_por_cantidades, key=len, reverse=True)#les ordeno para que mejore la visualizacoin

  df_csv=pedidos_a_exportar(pedidos) #genero el df listo para exportarlo
  return render_template('generar_pedidos.html', pedidos_por_cantidades=pedidos_por_cantidades, penalizacion=penalizacion, df_csv=df_csv)
  
  
@app.route('/exportar_csv', methods=['GET', 'POST'])
@login_required
def exportar_csv():
    #si el usuario pone directamente la url en el navegador
  if request.method == 'GET':
    return redirect(url_for('inicio'))
  
  df_json = request.form.get('df_csv') # Recibo el DataFrame desde el formulario
  df = pd.read_json(df_json)
  
# Convierte el DataFrame a un archivo CSV en memoria
  csv_buffer = BytesIO()
  df.to_csv(csv_buffer, index=False, encoding='utf-8')
  csv_buffer.seek(0)

  ahora=datetime.now()
  timestamp = ahora.strftime('%Y%m%d_%H%M%S')
  nombre_archivo = f'pedidos{timestamp}.csv'
#Devuelvo el archivo CSV de descarga
  return send_file(csv_buffer, mimetype='text/csv', as_attachment=True, download_name=nombre_archivo)
  
  
@app.route("/Historico_pedidos")
@login_required
def historico_pedidos():
  df=obtener_Datos('Historico_Pedidos.csv')
#df=conection.crearconexion('PEDIDOS_BRIKS')
#Hago un maestro de Pedidos para mostrar los pedidos
  df_pedidos_unicos = df.drop_duplicates(subset=["Pedido"])[["Pedido", "Fecha"]].set_index('Pedido')
  return render_template('historico_pedidos.html', df=df, df_pedidos_unicos=df_pedidos_unicos)

  
@app.route('/exportar_csv_historico', methods=['GET', 'POST'])
@login_required
def exportar_csv_historico():
    #Si recibo la url directamente por el navegador
  if request.method == 'GET':
    return redirect(url_for('inicio'))
  try:
    #Recojo todos los Pedido_ (los que han marcado)
    pedidos_seleccionados = [key.split('_')[1] for key in request.form if key.startswith('pedido_')]
    df_json_str = request.form.get('df')
    df_json = json.loads(df_json_str)
    df = pd.DataFrame.from_dict(df_json)
    pedidos_seleccionados = [int(pedido) for pedido in pedidos_seleccionados] #lo convierto a int para poder hacer la comparacion
    df = df[df['Pedido'].isin(pedidos_seleccionados)] #Nos quedamos solo con los que han seleccionado.
    df = df.drop('Fecha', axis=1) #Elimino la columna fecha
    
    # Convierte el DataFrame a un archivo CSV en memoria (modo binario)
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_buffer.seek(0)
    
    ahora=datetime.now()
    timestamp = ahora.strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f'pedidos_sap{timestamp}.csv'
    # Devuelvo el archivo CSV a descargar
    return send_file(csv_buffer, mimetype='text/csv', as_attachment=True, download_name=nombre_archivo)
  except BadRequestKeyError as e:
    print(f'Error: {e}')
    return 'Error en la solicitud', 400  # Retorna un código de estado HTTP 400 Bad Request


#Pagina acerca de
@app.route("/Acerca_de")
@login_required
def acerca_de():
  return render_template('acerca_de.html')

#Pagina para descargar el manual de usuario
@app.route('/descargar_manual')
def descargar_manual():
    pdf_path = 'static/archivos/Manualdeusuario.pdf'
    return send_file(pdf_path, as_attachment=True, download_name="Manual de usuario.pdf")

#Funcion para controlar que no esta logueado
@app.errorhandler(401)
def status_401(error):
  return redirect(url_for('login'))
    
#Funcion para controlar cuando intentan entrar a una url que no existe
@app.errorhandler(404)
def status_404(error):
  return render_template('error404.html')


if __name__ == "__main__":
  app.config.from_object(config['development'])
  app.register_error_handler(401, status_401)
  app.register_error_handler(404, status_404)
  
  app.run(debug=False)