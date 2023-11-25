import json
import config
import psycopg2.extras
import logging
from flask_login import LoginManager, login_user, logout_user, login_required
from flask import Flask, render_template, request, redirect, url_for, flash, session
from operaciones import insertarOperacion
from operacionWu import  nuevaOperacionWuSolDao, nuevaOperacionWuDolarDao, obtenerOperacionId
from utilitario import obtenerFechaActual, obtenerFechaAnterior
from datetime import date, datetime, timedelta
from caja import actualizarCajaBanco, actualizarCajaDolar, validarAperturaCaja, actualizarEfectivoCaja
import locale

def calcularComision(monto, bancoid):
    logging.info('Inicio calcularComision')
    Select = "select VALOR1, VALOR2  from CATALOGO where CODIGO='REGLA_COMISION_1'"
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_campos = cur.fetchall()
    monto_regla = float(list_campos[0][0])
    comision_regla = float(list_campos[0][1])
    comision=0
    if bancoid==13 or bancoid==6: #BCP
        if monto <=500:
            comision=1
        if monto <=1000 and monto > 500:
            comision=2
        else:
            comision=round(monto/monto_regla)
    else:
        if monto >= 500 and monto <=999:
            comision=1
        if monto >= 1000 and monto <= 1499:
            comision = 2
        if monto >= 1500 and monto <= 1999:
            comision = 3
        if monto >= 2000 and monto <= 2499:
            comision = 4
        if monto >= 2000 and monto <= 2499:
            comision = 4
        if monto >= 2500 and monto <= 2999:
            comision = 5
        if monto >= 3000 and monto <= 3499:
            comision = 6
        if monto >= 3500 and monto <= 3999:
            comision = 7
        if monto >= 4000 and monto <= 4499:
            comision = 8
        if monto >= 4500 and monto <= 4999:
            comision = 9
    logging.info('comision: ' + str(comision))
    logging.info('Fin calcularComision')
    return comision

@login_required
def ingresosEgresos():
        logging.info('---------------------Inicio de ingresosEgresos---------------------')
        if request.method == 'POST':
            if request.form['accion_btn'] == 'ingreso':
                Operacionid = obtenerOperacionId()
                TipoOperacionId = 2  # 1:Salida de Efectivo (RETIRO) e Ingreso de Efectivo en el POS
                Comentario = "Comentario:" + request.form['comentario'] + "|Caja Descripcion:" + str(
                    session['cajaDescripcion']) + "|CajaSolesId:" + str(
                    session['cajaSolesId']) + "|CajaDolaresId:" + str(session['cajaDolaresId'])
                Comision = 0
                Monto = float(request.form['comision'])

                if int(request.form['BancoId'])==26 or int(request.form['BancoId']) == 27: #WESTER UNION
                    if int(request.form['BancoId'])==26: #WESTER UNION (SOLES) - BCP
                        BancoId = int(request.form['BancoId'])
                        TipoMonedaId = int(1)  # 1:Sol
                        Montosolcaja =0
                        nuevaOperacionWuSolDao(Operacionid, BancoId, TipoOperacionId, Monto, Montosolcaja, Comision,
                                               Comentario)
                        flash('Se registro con exito la comisión.', 'success')
                    if int(request.form['BancoId']) == 27: #WESTER UNION (DOLARES) - BCP
                        BancoId = int(request.form['BancoId'])
                        TipoMonedaId = int(2)  # 1:Sol
                        nuevaOperacionWuDolarDao(Operacionid, BancoId, TipoOperacionId, Monto, Comision, Comentario, 0, 0, 0,
                                                 0, TipoMonedaId)
                        flash('Se registro con exito la comisión.', 'success')
                else: #AGENTE
                    registrarComision(request)

            if request.form['accion_btn'] == 'egreso':
                registrarGasto(request)
            return redirect(url_for('ingresosEgresos'))
        else:
            conn = config.get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            fecha_actual = datetime.now()
            # Obtener el nombre del mes
            mesSelectedId = fecha_actual.month
            scriptMeses = "select catalogo_id, codigo, nombre, valor1, descripcion from catalogo where codigo ='MES'"
            cur.execute(scriptMeses)  # Execute the SQL
            list_meses = cur.fetchall()

            logging.info('---------------------Fin de ingresosEgresos---------------------')
            return render_template('administrativo/IngresoEgreso.html',
                                   mesSelectedId=mesSelectedId,
                                   list_meses=list_meses)

def registrarComision(request):
    logging.info('---------------------Inicio de registrarComision---------------------')
    try:
        TipoOperacionId = 1 #1:Salida de Efectivo (RETIRO) e Ingreso de Efectivo en el POS
        TipoMonedaId = int(1)  # 1:Sol
        Monto = 0
        Comision = float(request.form['comision'])
        FechaOperacion = obtenerFechaActual()
        FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour,
                                                                                           minutes=datetime.now().minute,
                                                                                           seconds=datetime.now().second)
        numerooperacion = 1
        BancoId = int(request.form['BancoId'])
        ComisionBanco = 0
        Usuarioid = session['usuarioid']
        Comentario = "Comentario:" + request.form['comentario'] + "|Caja Descripcion:" + str(
            session['cajaDescripcion']) + "|CajaSolesId:" + str(
            session['cajaSolesId']) + "|CajaDolaresId:" + str(session['cajaDolaresId'])

        Saldo = actualizarCajaBanco(TipoOperacionId, BancoId, Monto, Comision, TipoMonedaId, ComisionBanco)
        insertarOperacion(
                        TipoOperacionId,
                        Monto,
                        Comision,
                        FechaOperacion,
                        Comentario,
                        TipoMonedaId,
                        BancoId,
                        Saldo,
                        Usuarioid,
                        numerooperacion,
                        ComisionBanco
                    )
        flash('Se registro con exito la comisión.', 'success')
    except Exception as e:
        flash('Se registro con error la comisión. Error:' + str(e) + '. Verificar si tienes aperturado tu CAJA - AGENTE', 'error')
        logging.error(e)
    finally:
        logging.info('---------------------Fin de registrarComision---------------------')

def registrarGasto():
    logging.info('---------------------Inicio de registrarGasto---------------------')
    try:
        TipoOperacionId = 1  # 1:Salida de Efectivo (RETIRO) e Ingreso de Efectivo en el POS
        TipoMonedaId = int(1)  # 1:Sol
        Monto = request.form['monto']
        Comision = 0
        FechaOperacion = obtenerFechaActual()
        FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour,
                                                                                           minutes=datetime.now().minute,
                                                                                           seconds=datetime.now().second)
        numerooperacion = 1
        BancoId = int(request.form['BancoId'])
        ComisionBanco = 0
        Usuarioid = session['usuarioid']
        Comentario = request.form['comentario']
        Saldo = actualizarCajaBanco(TipoOperacionId, BancoId, Monto, Comision, TipoMonedaId, ComisionBanco)
        insertarOperacion(
            TipoOperacionId,
            Monto,
            Comision,
            FechaOperacion,
            Comentario,
            TipoMonedaId,
            BancoId,
            Saldo,
            Usuarioid,
            numerooperacion,
            ComisionBanco
        )

    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('---------------------Fin de registrarGasto---------------------')

@login_required
def listaOperacionAdmin():
    logging.info('---------------------Inicio de listaOperacion---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fechaActual = str(obtenerFechaActual())
    s = "SELECT " \
        "op.operacionid, " \
        "b.nombre, " \
        "top.nombre, " \
        "op.monto, " \
        "op.comision, " \
        "op.fechaoperacion, " \
        "tm.nombre, " \
        "op.comentario, " \
        "op.saldo, " \
        "usu.nombre, " \
        "usu.usuarioid, " \
        "top.tipooperacionid, " \
        "ROW_NUMBER () OVER(ORDER BY operacionid DESC) as indice" \
        " FROM operaciones as op " \
        "left  join  tipomoneda tm on tm.tipomonedaid = op.tipomonedaid " \
        "left join tipooperacion top on top.tipooperacionid = op.tipooperacionid " \
        "left join banco b on b.bancoid =op.bancoid " \
        "left join usuario usu on usu.usuarioid =op.usuarioid "

    if request.method == 'POST':
        mes = request.form['Mes']
        mesSelected = mes.split('|')[1]
        mesSelectedId = mes.split('|')[0]
        s = s + " where op.estado isnull and op.comentario like '%%COMISION:"+mesSelected+"%%'"
        s = s + " order by op.operacionid DESC "
    else:
        locale.setlocale(locale.LC_TIME, 'es_ES.utf-8')
        fecha_actual = datetime.now()
        # Obtener el nombre del mes
        mesSelected = fecha_actual.strftime("%B")
        mesSelected = mesSelected.replace(" ", "")
        mesSelectedId = fecha_actual.month

        s = s + " where op.estado isnull and op.comentario like '%%COMISION:"+mesSelected+"%%'"
        s = s + " order by op.operacionid DESC "

        # SelectSumaComision = "SELECT sum(comision), sum(numerooperacion) FROM operaciones where fechaoperacion between %s and  %s"

    try:
        cur.execute(s)
    except Exception as ex:
        raise Exception(ex)

    list_operaciones = cur.fetchall()
    scriptTipoOperacion = "SELECT tipooperacionid, nombre FROM tipooperacion order by tipooperacionid"
    cur.execute(scriptTipoOperacion)  # Execute the SQL
    list_tipooperaciones = cur.fetchall()
    list_tipooperaciones.insert(0, [0, "TODOS"])

    scriptMeses = "select catalogo_id, codigo, nombre, valor1, descripcion from catalogo where codigo ='MES'"
    cur.execute(scriptMeses)  # Execute the SQL
    list_meses = cur.fetchall()
    list_meses.insert(0, [0, "MES", "TODOS", 0, ""])

    #cur.execute(SelectSumaComision, (fechaInicio, fechaFin + " 23:59:59"))
    #sumaComision = cur.fetchall()


    logging.info('---------------------Fin de listaOperacion---------------------')
    return render_template('administrativo/ListaOperacion.html',
                           list_operaciones=list_operaciones,
                           list_meses=list_meses,
                           mesSelectedId=str(mesSelectedId),
                           fechaActual=fechaActual
                           )
