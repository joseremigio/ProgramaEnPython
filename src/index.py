from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from datetime import date, datetime, timedelta
import logging
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required
import psycopg2.extras
# Models:
from models.ModelUser import ModelUser
from flask_cors import CORS
import asistencia

# Entities:
from models.entities.User import User
import operaciones
import operacionWu
import scrapyWu
import caja
import cajaWu
import capital
import config
import tipoCambio
import publicidad
import scrapyTipoCambio
import ingresoEgreso
import remesa
from utilitario import obtenerFechaActual, obtenerFechaAnterior

# Configuración del logger
log_filename= "log/log_file" + datetime.now().strftime("%Y-%m-%d-%H") + ".log"
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#cProfile.run("app.run(debug=True)")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.add_url_rule('/nuevaOperacion', view_func=operaciones.nuevaOperacion, methods=['POST', 'GET'])
app.add_url_rule('/imprimirNuevaOperacion/<string:monto>/<string:comision>/<string:tipoOperacion>', view_func=operaciones.impresion, methods=['GET'])
app.add_url_rule('/delete/<string:id>/<string:monto>/<string:comision>/<string:tipoOperacionId>/<string:bancoId>/<string:comisionbancoid>', view_func=operaciones.delete_operacion, methods=['GET'])
app.add_url_rule('/transferir', view_func=operaciones.transferir, methods=['POST', 'GET'])
app.add_url_rule('/compraventadolar', view_func=operaciones.compraventadolar, methods=['POST', 'GET'])
app.add_url_rule('/compraventadolarimpresion/<string:tipoCambioValor>/<string:montoEnviar>/<string:montoRecibir>/<string:tipoMonedaEnviar>/<string:tipoMonedaRecibir>/<string:Fecha>/<string:operacionid>', view_func=operaciones.compraventadolarimpresion, methods=['POST', 'GET'])

app.add_url_rule('/cajaApertura', view_func=caja.cajaApertura, methods=['POST', 'GET'])
app.add_url_rule('/cajaCierre', view_func=caja.cajaCierre)
#app.add_url_rule('/add_cajaApertura', view_func=caja.add_cajaApertura, methods=['POST'])
app.add_url_rule('/add_cajaCierre', view_func=caja.add_cajaCierre, methods=['POST'])
app.add_url_rule('/cargarImagen', view_func=caja.cargarImagen, methods=['POST', 'GET'])



app.add_url_rule('/capital', view_func=capital.capital)
app.add_url_rule('/add_capital', view_func=capital.add_capital, methods=['POST'])

#operaciones Wu
app.add_url_rule('/nuevaOperacionWu', view_func=operacionWu.nuevaOperacionWu, methods=['POST', 'GET'])
app.add_url_rule('/eliminar/<string:id>', view_func=operacionWu.eliminar, methods=['GET'])
app.add_url_rule('/nuevaOperacionWUDolar', view_func=operacionWu.nuevaOperacionWuDolar, methods=['POST'])
app.add_url_rule('/nuevaOperacionWUSol', view_func=operacionWu.nuevaOperacionWuSol, methods=['POST'])
app.add_url_rule('/listaOperacionWu', view_func=operacionWu.listaOperacion, methods=['POST', 'GET'])
app.add_url_rule('/transferirWu', view_func=operacionWu.transferirWu, methods=['POST', 'GET'])
app.add_url_rule('/aperturaCajaWu', view_func=cajaWu.apertura, methods=['POST', 'GET'])
app.add_url_rule('/cierreCajaWu', view_func=cajaWu.cierre, methods=['POST', 'GET'])
app.add_url_rule('/compraventadolarWu', view_func=operacionWu.compraventadolarWu, methods=['POST', 'GET'])

#remesa
app.add_url_rule('/registraRemesa', view_func=remesa.registraRemesa, methods=['POST', 'GET'])
app.add_url_rule('/listaRemesa', view_func=remesa.listaRemesa, methods=['POST', 'GET'])

#scrapyWu
app.add_url_rule('/boletaWu', view_func=scrapyWu.boletaWu, methods=['POST', 'GET'])
app.add_url_rule('/ejemplo', view_func=scrapyWu.ejemplo, methods=['POST', 'GET'])

#tipoCambio
app.add_url_rule('/api/tipocambio/', view_func=tipoCambio.consultaTipoCambio, methods=['GET'])
app.add_url_rule('/api/tipocambio/insertar/<string:valor_venta>/<string:valor_compra>/<string:modalidadid>', view_func=tipoCambio.insertar, methods=['GET'])


app.add_url_rule('/tipocambio/', view_func=tipoCambio.load, methods=['POST', 'GET'])

#publicidad
app.add_url_rule('/showPublicidad/', view_func=publicidad.showPublicidad, methods=['GET'])
app.add_url_rule('/showTipoCambio/', view_func=publicidad.showTipoCambio, methods=['GET'])

#asistencia

#app.add_url_rule('/display_video/<filename>', view_func=publicidad.display_video, methods=['GET'])
#UPLOAD_FOLDER = 'static/uploads/'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


#scrapy
app.add_url_rule('/scrapy/', view_func=scrapyTipoCambio.obtenerYactualizarTipoCambio, methods=['GET'])

#Administrativos
app.add_url_rule('/ingresosEgresos/', view_func=ingresoEgreso.ingresosEgresos, methods=['POST', 'GET'])
app.add_url_rule('/listaOperacionAdmin/', view_func=ingresoEgreso.listaOperacionAdmin, methods=['POST', 'GET'])

#app.logger.setLevel(logging.ERROR)

app.secret_key = "cairocoders-ednalan"

csrf = CSRFProtect()
login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    logging.info('Inicio de load_user')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    logging.info('Fin de load_user')
    #cur = config.get_db_connection()
    return ModelUser.get_by_id(cur, id)

@app.route('/', methods=['GET', 'POST'])
def index():

    logging.info('Inicio de index')
    ipAddress = request.remote_addr
    session['ipAddress'] = ipAddress
    logging.info('Fin de index')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        logging.info('Inicio de login')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        listaCajas = caja.listarCaja()
        if request.method == 'POST':
            user = User(0, request.form['username'], request.form['password'],"",0)
            logged_user = ModelUser.login(cur, user)
            if logged_user != None:
                if logged_user.password:
                    login_user(logged_user)
                    session['usuario'] = logged_user.username
                    session['nombre'] = logged_user.fullname
                    session['rolid'] = logged_user.rolid
                    session['usuarioid'] = logged_user.id
                    catalogoId = request.form['catalogoId']
                    caja.asignacionCaja(catalogoId)
                    asistencia.registrar()
                    return redirect(url_for('home'))
                else:
                    flash("Contraseña invalida")
                    return render_template('login.html', listaCajas=listaCajas)
            else:
                flash("Usuario no encontrado")
                return render_template('login.html', listaCajas=listaCajas)
        else:
            return render_template('login.html', listaCajas=listaCajas)
    finally:
        logging.info('Fin de login')

@app.route('/logout')
def logout():
    logging.info('Inicio de logout')
    asistencia.actualizar()
    logout_user()
    session['cajaSolesId'] = ""
    session['cajaDolaresId'] = ""
    logging.info('Fin de logout')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    logging.info('Inicio de profile')
    if request.method == 'POST':
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        logged_user = ModelUser.update(cur, session['rolid'], request.form['nombre'], request.form['contrasena'])
        conn.commit()
        session['nombre'] = request.form['nombre']
        flash('Actualización con exito','success')
        logging.info('Fin de profile')
        return render_template('usuario.html', nombre=request.form['nombre'])
    else:
        return render_template('usuario.html', nombre=session['nombre'])


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    logging.info('Inicio de home')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fechaActual = str(obtenerFechaActual())
    RecargaSaldo = True
    soloMisOperaciones = True
    if request.method == 'POST':
        fechaInicio = request.form['startDate']
        fechaFin = request.form['endDate']
        BancoId = request.form['BancoId']
        TipoOperacionId = request.form['TipoOperacionId']
        try:
            RecargaSaldo = request.form.get("recargaSaldo") != None
        finally:
            RecargaSaldo = RecargaSaldo

        try:
            soloMisOperaciones = request.form.get("soloMisOperaciones") != None
        finally:
            soloMisOperaciones = soloMisOperaciones

        s = "SELECT op.operacionid, top.nombre, op.monto, op.comision, op.fechaoperacion, op.comentario, tm.nombre, b.nombre, op.comentario, op.saldo, top.tipooperacionid, op.bancoid, ROW_NUMBER () OVER(ORDER BY operacionid DESC) as indice, usu.nombre, usu.usuarioid, op.numerooperacion, op.comisionbancoid " \
            "FROM operaciones as op " \
            "left  join  tipomoneda tm on tm.tipomonedaid = op.tipomonedaid " \
            "left join tipooperacion top on top.tipooperacionid = op.tipooperacionid  " \
            "left join banco b on b.bancoid =op.bancoid " \
            "left join usuario usu on usu.usuarioid =op.usuarioid "
        s = s + "where op.estado isnull and op.fechaoperacion between %s and  %s "
        SelectSumaComision = "SELECT sum(comision), sum(numerooperacion) " \
                             "FROM operaciones " \
                             "where estado isnull and fechaoperacion between %s and  %s"
        if BancoId=='0':
            SelectSumaComision = SelectSumaComision
        else:
            s = s + " and b.bancoid= " + str(BancoId)
            SelectSumaComision = SelectSumaComision + " and bancoid=" + BancoId

        if TipoOperacionId=='0':
            SelectSumaComision = SelectSumaComision
        else:
            s = s + " and op.tipooperacionid= " + str(TipoOperacionId)
            SelectSumaComision = SelectSumaComision + " and tipooperacionid=" + TipoOperacionId

        if RecargaSaldo:
            s = s + " and op.comentario not like '%%RECARGA%%' "
        if soloMisOperaciones:
            s = s + " and op.usuarioid=" + str(session['usuarioid'])
            SelectSumaComision= SelectSumaComision + " and usuarioid=" + str(session['usuarioid'])


        s = s + "order by op.operacionid DESC "
        #ur.execute(s, (fechaInicio, fechaFin + " 23:59:59"))
        try:
            cur.execute(s, (fechaInicio, fechaFin + " 23:59:59"))
        except Exception as ex:
            raise Exception(ex)

    else:
        fechaInicio=str(obtenerFechaActual())
        #fechaFin=(date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        fechaFin = fechaInicio
        s = "SELECT op.operacionid, top.nombre, op.monto, op.comision, op.fechaoperacion, op.comentario, tm.nombre, b.nombre, op.comentario, op.saldo, top.tipooperacionid, op.bancoid, ROW_NUMBER () OVER(ORDER BY operacionid DESC) as indice, usu.nombre, usu.usuarioid, op.numerooperacion, op.comisionbancoid " \
            "FROM operaciones as op " \
            "left join  tipomoneda tm on tm.tipomonedaid = op.tipomonedaid " \
            "left join tipooperacion top on top.tipooperacionid = op.tipooperacionid " \
            "left join banco b on b.bancoid =op.bancoid " \
            "left join usuario usu on usu.usuarioid =op.usuarioid "
        s = s + "where op.estado isnull and op.fechaoperacion between %s and  %s "
        s = s + " and op.comentario not like '%%RECARGA%%' "

        SelectSumaComision = "SELECT sum(comision), sum(numerooperacion) " \
                             "FROM operaciones " \
                             "where estado isnull and fechaoperacion between %s and  %s"


        if soloMisOperaciones:
            s = s + " and op.usuarioid=" + str(session['usuarioid'])
            SelectSumaComision = SelectSumaComision + " and usuarioid=" + str(session['usuarioid'])

        s = s + " order by op.operacionid DESC "
        try:
            cur.execute(s, (fechaInicio, fechaFin + " 23:59:59"))
        except Exception as ex:
            raise Exception(ex)
        BancoId = '0'
        TipoOperacionId = '0'

    list_operaciones = cur.fetchall()

    scriptBanco = "SELECT bancoid, nombre FROM banco where eswu=0 order by bancoid"
    cur.execute(scriptBanco)
    list_banco = cur.fetchall()
    list_banco.insert(0, [0, "TODOS"])

    scriptTipoOperacion = "SELECT tipooperacionid, nombre FROM tipooperacion order by tipooperacionid"
    cur.execute(scriptTipoOperacion)  # Execute the SQL
    list_tipooperaciones = cur.fetchall()
    list_tipooperaciones.insert(0, [0, "TODOS"])

    cur.execute(SelectSumaComision, (fechaInicio, fechaFin + " 23:59:59"))
    sumaComision = cur.fetchall()


    #obtenerTipoCambioTuCambista()
    logging.info('Fin de home')
    return render_template('index.html', list_operaciones=list_operaciones, list_banco=list_banco, fechaInicio=fechaInicio, fechaFin=fechaFin, bancoSelectedId=BancoId, tipoOperacionSelectedId=TipoOperacionId,fechaActual=fechaActual, sumaComision=sumaComision, list_tipooperaciones=list_tipooperaciones,recargaSaldo=RecargaSaldo, soloMisOperaciones=soloMisOperaciones)

@app.route('/reporte/<string:anio>/<string:mes>')
@login_required
def reporte(anio, mes):
    logging.info('Inicio de reporte')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    Select = "select sum(montoinicial) as montoinicial, sum(montofinalcalculado) as montofinalcalculado, sum(montofinalreal) as montofinalreal, fecha, EXTRACT(year from fecha) as anio, EXTRACT(month from fecha) as mes, EXTRACT(day from fecha) as dia  " \
             "from  caja "
    Select = Select + " where estado isnull and EXTRACT(year from fecha)=" + anio + " and EXTRACT(month from fecha)=" + mes
    Select = Select + " group by fecha order by dia"
    cur.execute(Select)  # Execute the SQL
    list_cajas = cur.fetchall()

    montosiniciales = []
    montosfinalcalculados = []
    montosfinalreales = []
    fechas = []
    meses = []
    dias = []

    posicion = 1
    for item in list_cajas:
        montosiniciales.insert(posicion, item[0])
        montosfinalcalculados.insert(posicion, item[1])
        montosfinalreales.insert(posicion, item[2])
        fechas.insert(posicion, item[3])
        meses.insert(posicion, item[5])
        dias.insert(posicion, item[6])
        posicion = posicion+1

    logging.info('Fin de reporte')
    return render_template('reporte/reporte.html', dias=dias , montosiniciales=montosiniciales, montosfinalcalculados=montosfinalcalculados, montosfinalreales=montosfinalreales, list_cajas=list_cajas)

@app.route('/asistencia/<string:anio>/<string:mes>')
@login_required
def reporteAsistencia(anio, mes):
    try:
        logging.info('---------------------Inicio de load---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        RolId = session['rolid']
        if RolId==1: #Obtenemos todos los usuarios si el Rol es administrador:1
            UsuarioId ='select usuarioid from usuario'
        else:
            UsuarioId = session['usuarioid']

        Select = "SELECT " \
                 "us.nombre, " \
                 "a.fecha, " \
                 "TO_CHAR(a.horaingreso, 'HH24:MI:SS'), " \
                 "TO_CHAR(a.horasalida, 'HH24:MI:SS'), " \
                 "TO_CHAR((a.horasalida - a.horaingreso), 'HH24:MI:SS') as diferencia " \
                 "from asistencia a " \
                 "left join usuario us on us.usuarioid =a.usuarioid " \
                 "where a.usuarioid IN(" + str(UsuarioId) + ")" + " " \
                 "and EXTRACT(MONTH FROM a.fecha)= '" + mes + "'" + " and EXTRACT(YEAR FROM a.fecha)= '" + anio + "' " \
                 "order by us.nombre, a.fecha"
        cur.execute(Select)
        listaAsistencia = cur.fetchall()

    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('---------------------Fin de load------------------------')
        return render_template('reporte/asistencia.html', listaAsistencia=listaAsistencia, mes=mes, anio=anio)


@app.route('/get_textos')
def get_textos():
    # Lee el contenido del archivo JSON
    with open('static/buenas_practicas.json', 'r') as file:
        data = file.read()
    return jsonify(data)

if __name__ == '__main__':
    #app.run()
    app.run(host='0.0.0.0', port=8000, debug=False) #para acceder desde la misma red mediante la IP

