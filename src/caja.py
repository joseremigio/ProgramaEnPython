from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import config
import psycopg2
import psycopg2.extras
from decimal import Decimal
from flask_login import LoginManager, login_user, logout_user, login_required
from tipoCambio import consultarTipoCambioReferencia
from utilitario import obtenerFechaActual, obtenerFechaAnterior
from ocr.ocr import obtenerNumero, obtenerTexto

import os
from werkzeug.utils import secure_filename

#import pywhatkit


from datetime import date, datetime, timedelta

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def validarAperturaCaja():
    conn = config.get_db_connection()
    Fecha = str(obtenerFechaActual())
    Select = "SELECT count(cajaid) from caja as ca left join banco ba on ba.bancoid =ca.bancoid " \
             "where ca.estado isnull and ba.eswu=0 and fecha= '" + Fecha + "'"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_caja = cur.fetchall()
    if int(list_caja[0][0]) == 0:
        logging.info('Ingreso al SUB IF')
        flash('No se tiene aperturada caja para la fecha:' + Fecha, 'error')
        return False
    return True

def selectCajaApertura (fechaSeleccionada):
    logging.info('---------------------Inicio de selectCajaApertura---------------------')
    fechaDeHoy = str(obtenerFechaActual())
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    scriptBanco = "SELECT " \
                  "ba.bancoid, " \
                  "ba.nombre, " \
                  "COALESCE((ca.montofinalreal), 0) AS montofinalreal, " \
                  "ca.fecha " \
                  "FROM banco ba "
    scriptBanco = scriptBanco + "left join caja ca on ca.bancoid =ba.bancoid  where ca.estado isnull and ba.eswu =0"
    scriptBanco = scriptBanco + "order by ca.fecha desc, ba.orden "
    scriptBanco = scriptBanco + "limit (select count(ba.bancoid) from banco ba where ba.eswu =0) "
    cur.execute(scriptBanco)  # Execute the SQL
    list_banco = cur.fetchall()
    Select = "SELECT " \
             "c.cajaid, " \
             "c.montoinicial, " \
             "c.montofinalcalculado, " \
             "c.montofinalreal, " \
             "b.nombre " \
             "from caja c " \
             "left join banco b on b.bancoid =c.bancoid "
    Select = Select + "where c.estado isnull and b.eswu = 0 and c.fecha= '" + str(fechaSeleccionada) + "'"
    Select = Select + " order by c.cajaid"
    cur.execute(Select)
    list_cajas = cur.fetchall()
    logging.info('---------------------Fin de selectCajaApertura---------------------')
    return render_template('cajaApertura.html', list_banco=list_banco, fecha=fechaSeleccionada, list_cajas=list_cajas, fechaDeHoy=fechaDeHoy)

@login_required
def cajaCierre():
    logging.info('---------------------Inicio de cajaCierre---------------------')
    fecha = str(obtenerFechaActual())
    return selectCajaCierre(fecha)

def selectCaja (fechaSeleccionada):
    logging.info('---------------------Inicio de selectCaja---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Total por banco
    Select = "SELECT " \
             "c.cajaid, " \
             "c.montoinicial, " \
             "c.montofinalcalculado, " \
             "c.montofinalreal, " \
             "b.nombre, " \
             "c.comisionbanco, " \
             "c.montototalcalculado, " \
             "c.montodolarsol, " \
             "c.bancoid, " \
             "c.montodolarsolcalculado, " \
             "c.montodolarsolreal, " \
             "(select sum(numerooperacion) from operaciones op where op.estado isnull and op.fechaoperacion between '" + fechaSeleccionada + " 00:00:00' and '" + fechaSeleccionada + " 23:59:59' and op.bancoid=c.bancoid and op.comentario not like '%RECARGA%'), " \
             "c.url " \
             "from caja c " \
             "left join banco b on b.bancoid =c.bancoid " \
             "left join operaciones o on o.bancoid =c.bancoid  "
    Select = Select + "where c.estado isnull and b.eswu = 0 and c.fecha= '" + fechaSeleccionada + "' and c.bancoid not in (15, 17)"
    Select = Select + " group by c.cajaid, c.montoinicial, c.montofinalcalculado, c.montofinalreal, b.nombre, " \
                      " c.comisionbanco, c.montototalcalculado, c.montodolarsol, c.bancoid, c.montodolarsolcalculado, " \
                      " c.montodolarsolreal,b.orden,c.url" \
                      " order by b.orden"
    cur.execute(Select)
    list_cajas = cur.fetchall()
    return list_cajas

def selectCajaCierre (fechaSeleccionada):
    logging.info('---------------------Inicio de selectCajaCierre---------------------')
    fechaDeHoy = str(obtenerFechaActual())
    list_cajas = selectCaja(fechaSeleccionada)
    # Suma de todos los bancos
    suma_caja = selectSumaDeCaja(fechaSeleccionada)
    logging.info('---------------------Fin de selectCajaCierre---------------------')
    return render_template('cajaCierre.html', list_cajas=list_cajas, fecha=fechaSeleccionada, suma_caja=suma_caja, fechaDeHoy=fechaDeHoy)

def selectSumaDeCaja (fechaSeleccionada):
    logging.info('Inicio de selectSumaDeCaja')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #Select = "SELECT sum(c.montoinicial) as " \
    #         "sumamontoinicial , sum(c.montofinalcalculado) as sumamontofinalcalculado, sum(c.montofinalreal) as sumamontofinalreal, sum(c.comisionbanco) as sumacomisionbanco, sum(c.montototalcalculado) as sumamontototalcalculado from caja c  "
    #Select = Select + "where c.bancoid not in (15, 17) and c.fecha= '" + fechaSeleccionada + "'"
    Select = "select" \
			" ROUND(cast(sum(T.sumamontoinicial) AS numeric),2) as sumamontoinicial,  " \
            " ROUND(cast(sum(T.sumamontofinalcalculado) AS numeric),2) as sumamontofinalcalculado , " \
			" ROUND(cast(sum(T.sumamontofinalreal) AS numeric),2) as sumamontofinalreal,  " \
            " ROUND(cast(sum(T.sumacomisionbanco) AS numeric),2) as sumacomisionbanco, " \
			" ROUND(cast(sum(T.sumamontototalcalculado)  AS numeric),2) as sumamontototalcalculado " \
			" from" \
			" (" \
			" SELECT sum(c.montoinicial) as sumamontoinicial , sum(c.montofinalcalculado) as sumamontofinalcalculado," \
			" sum(c.montofinalreal) as sumamontofinalreal, sum(c.comisionbanco) as sumacomisionbanco," \
			" sum(c.montototalcalculado) as sumamontototalcalculado" \
			" from caja c  left join banco b on b.bancoid = c.bancoid  " \
             "where c.estado isnull and b.eswu = 0 and c.bancoid not in (15, 17, 16, 18) and c.fecha= '" + fechaSeleccionada + "'" +" group by c.fecha" \
			" union" \
			" SELECT sum(c.montodolarsol) as sumamontoinicial , sum(c.montodolarsolcalculado) as sumamontofinalcalculado," \
			" sum(c.montodolarsolcalculado) as sumamontofinalreal, sum(c.comisionbanco) as sumacomisionbanco," \
			" sum(c.montodolarsolcalculado) as sumamontototalcalculado" \
			" from caja c  left join banco b on b.bancoid = c.bancoid " \
            " where c.estado isnull and b.eswu = 0 and c.bancoid  in (16, 18) and c.fecha= '" + fechaSeleccionada + "'" +" group by c.fecha)" \
	 	" T;"
    #--Se suma los montos totales de bancos menos las cajas de wester y cajes de $
    #--Se suma los totales solo de la caja principal y secundaria de Dolares convertidos en S./
    cur.execute(Select)
    suma_caja = cur.fetchall()

    try:
        utilidad = suma_caja[0][2] - Decimal(obtenerCapital()[0][0])
        ganacia = suma_caja[0][2] - suma_caja[0][0]
        suma_caja.insert(3,[utilidad])
        suma_caja.insert(4,[ganacia])
    finally:
        logging.info('Fin de selectSumaDeCaja')
        return suma_caja

@login_required
def cajaApertura():
    logging.info('---------------------Inicio de cajaApertura---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if request.method == 'POST':
            if request.form['accion_btn'] == 'registrar':  # registrar
                Fecha = request.form['fecha']
                '''
                Select = "SELECT count(cajaid) from caja as ca left join banco ba on ba.bancoid =ca.bancoid where ca.estado isnull and ba.eswu=0 and fecha= '" + Fecha + "'"
                cur.execute(Select)
                list_caja = cur.fetchall()
                if int(list_caja[0][0]) > 0:
                    flash('Ya se tiene aperturada caja para la fecha:' + Fecha, 'error')
                    return redirect(url_for('cajaApertura'))
                
                if validarAperturaCaja() == False:
                    return redirect(url_for('cajaApertura'))
                '''
                for item in request.form:
                    if item.isnumeric() and int(item) < 100:

                        MontoInicial = request.form[item]

                        MontoDolarSol = 0
                        if int(item) == 16 or int(item) == 17 or int(item) ==18: #bancos en $
                            valorCompraVirtual, valorVentaVirtual = consultarTipoCambioReferencia()
                            NuevoMontodolarsolcalculado = Decimal(MontoInicial) * Decimal(valorVentaVirtual)
                            MontoDolarSol = NuevoMontodolarsolcalculado
                        BancoId = int(item)
                        logging.info('MontoInicial: ' + str(MontoInicial))
                        logging.info('MontoDolarSol: ' + str(MontoDolarSol))
                        logging.info('BancoId: ' + str(BancoId))

                        Insert = "INSERT INTO caja (cajaid, bancoid, montoinicial, fecha, montofinalcalculado, montofinalreal, comisionbanco, montototalcalculado, montodolarsol, montodolarsolcalculado, montodolarsolreal) VALUES (nextval('caja_sq'),%s,%s,%s,%s,0,0,%s,%s,%s,0)"
                        cur.execute(Insert, (BancoId, MontoInicial, Fecha, MontoInicial, MontoInicial, float(MontoDolarSol), float(MontoDolarSol)))
                        conn.commit()

                flash('Apertura de caja  conexito con fecha: ' + Fecha, 'success')
                return redirect(url_for('cajaApertura'))
            if request.form['accion_btn'] == 'buscar':  # registrar
                return selectCajaApertura(request.form['fecha'])
            else:
                Fecha = request.form['fecha']
                #Delete = "DELETE FROM caja WHERE fecha = '" + Fecha + "' and bancoid in (select bancoid from banco where eswu=0)"
                #cur.execute(Delete)
                #conn.commit()
                #Delete = "DELETE FROM operaciones WHERE fechaoperacion between %s and  %s "
                #cur.execute(Delete, (Fecha, Fecha + " 23:59:59"))
                #conn.commit()

                Update = "UPDATE caja SET  estado= B'1' " \
                         "WHERE fecha = '" + Fecha + "' and bancoid in (select bancoid from banco where eswu=0)"
                cur.execute(Update)
                conn.commit()

                Update = "UPDATE operaciones SET  estado= B'1' " \
                         "WHERE fechaoperacion between %s and  %s "
                cur.execute(Update, (Fecha, Fecha + " 23:59:59"))
                conn.commit()

                flash('Se elimino con exito la caja y operaciones de la fecha: ' + Fecha, 'success')
                return selectCajaApertura(Fecha)
        else:
            fecha = str(obtenerFechaActual())
            return selectCajaApertura(fecha)
    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('Fin de cajaApertura')

@login_required
def add_cajaCierre():
    logging.info('---------------------Inicio de add_cajaCierre---------------------')

    if request.method == 'POST':
        logging.info('Ingreso al IF')
        if request.form['accion_btn']=='actualizar': #actualizar
            logging.info('Ingreso al SUB IF')
            for item in request.form:
                logging.info('Ingreso al FOR')
                if item.isnumeric():
                    logging.info('Ingreso al SUB SUB IF')
                    MontoFinalReal = request.form[item]
                    CajaId = int(item)
                    Modificado = datetime.now()
                    ModificadoPor  = session['usuarioid']
                    actualizarCajaMontoFinalReal(MontoFinalReal, Modificado, ModificadoPor, CajaId)

            flash('Cierre de caja con exito.', 'success')
            #pywhatkit.sendwhatmsg('+51969368883', 'Message 2', datetime.now().hour, datetime.now().minute + 1)
            return redirect(url_for('cajaCierre'))

        if request.form['accion_btn']=='cargarImagen': #cargarImagen
            cargarImagen(request)
        else: #buscar
            logging.info('Ingreso al ELSE')
            return selectCajaCierre(request.form['fechaCierre'])

def actualizarCajaMontoFinalReal(MontoFinalReal, Modificado, ModificadoPor, CajaId):
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    Update = "UPDATE caja SET montofinalreal=%s, modificado=%s, modificado_por=%s where cajaid=%s"
    cur.execute(Update, (MontoFinalReal, Modificado, ModificadoPor, CajaId))
    conn.commit()
    logging.info('CajaId: ' + str(CajaId))
    logging.info('MontoFinalReal: ' + str(MontoFinalReal))

def actualizarCajaBanco (TipoOperacionId, BancoId, Monto, Comision, TipoMonedaId, Comisionbancoid):
    try:
        logging.info('---------------------Inicio de actualizarCajaBanco---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        Fecha = str(obtenerFechaActual())
        Select = "SELECT cajaid, bancoid, montoinicial, montofinalreal, fecha, montofinalcalculado, estado, comisionbanco  from caja"
        Select = Select + " where estado isnull and fecha= '" + Fecha + "'" + " and bancoid=" + str(BancoId)
        cur.execute(Select)
        caja = cur.fetchall()

        CajaId = caja[0][0]
        Montoinicial = caja[0][2]
        Montofinalcalculado = caja[0][5]
        Comisionbanco = caja[0][7]

        logging.info('TipoMonedaId: ' + str(TipoMonedaId))
        logging.info('Monto: ' + str(Monto))
        logging.info('CajaId: ' + str(CajaId))
        logging.info('Montoinicial: ' + str(Montoinicial))
        logging.info('Montofinalcalculado: ' + str(Montofinalcalculado))
        logging.info('Comisionbanco: ' + str(Comisionbanco))

        if int(TipoOperacionId) == 1:  #salida de efectivo
            logging.info('Ingreso a IF')
            NuevoMontofinalcalculadoBanco = Montofinalcalculado + Monto
        else: #ingreso de efectivo
            logging.info('Ingreso a ELSE')
            NuevoMontofinalcalculadoBanco = Montofinalcalculado - Monto

        if int(Comisionbancoid) == 2: #comision ingreso en 2:banco 1:efectico
            logging.info('Ingreso a IF2')
            Comisionbanco = Comisionbanco + Comision
            Comision = 0

        MontoTotalCalculado= NuevoMontofinalcalculadoBanco+Comisionbanco

        actualizarMontoComisionCaja(NuevoMontofinalcalculadoBanco, Comisionbanco, MontoTotalCalculado, CajaId)

        #actualizarEfectivoCaja(Monto, Comision, TipoOperacionId)
        logging.info('---------------------Fin de actualizarCajaBanco---------------------')
        return NuevoMontofinalcalculadoBanco
    except Exception as ex:
        logging.info('actualizarCajaBanco - error: ' + str(ex))
        raise Exception(ex)


def actualizarMontoComisionCaja (montofinalcalculado, comisionbanco, montototalcalculado, cajaid):
    try:
        resultado = True
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        logging.info('---------------------Inicio de actualizarMontoComisionCaja---------------------')
        logging.info('montofinalcalculado: ' + str(montofinalcalculado))
        logging.info('comisionbanco: ' + str(comisionbanco))
        logging.info('montototalcalculado: ' + str(montototalcalculado))
        logging.info('CajaId: ' + str(cajaid))
        Update = "UPDATE caja SET montofinalcalculado=%s , comisionbanco=%s, montototalcalculado=%s where cajaid=%s"
        cur.execute(Update, (montofinalcalculado, comisionbanco, montototalcalculado, cajaid))
        conn.commit()
    except Exception as ex:
        resultado = False
        logging.info('actualizarMontoComisionCaja - error: ' + str(ex))
    finally:
        logging.info('---------------------Fin de actualizarMontoComisionCaja---------------------')
        return resultado

def actualizarEfectivoCaja (Monto, Comision, TipoOperacionId):
    try:
        logging.info('---------------------Inicio de actualizarEfectivoCaja---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        Fecha = str(obtenerFechaActual())

        #if session['rolid'] == 2:
        #    logging.info('Ingreso al IF')
        #    cajaEfectivo = 19 #caja secundario
        #else:
        #    logging.info('Ingreso al ELSE')
        #    cajaEfectivo = 7 #caja principal

        cajaEfectivo = session['cajaSolesId']

        Select = "SELECT cajaid, bancoid, montoinicial, montofinalreal, fecha, montofinalcalculado, estado, comisionbanco  from caja"
        Select = Select + " where estado isnull and fecha= '" + Fecha + "'" + " and bancoid=" + str(cajaEfectivo)
        cur.execute(Select)
        caja = cur.fetchall()
        CajaId = caja[0][0]
        Montoinicial = caja[0][2]
        Montofinalcalculado = caja[0][5]
        Comisionbanco = caja[0][7]

        logging.info('CajaId: ' + str(CajaId))
        logging.info('Montoinicial: ' + str(Montoinicial))
        logging.info('Antes Comisionbanco: ' + str(Comisionbanco))
        logging.info('Montofinalcalculado: ' + str(Montofinalcalculado))

        Comisionbanco= Comisionbanco + Comision

        logging.info('Despues Comisionbanco: ' + str(Comisionbanco))

        if int(TipoOperacionId) == 1:  # salida de efectivo
            logging.info('Ingreso al IF')
            NuevoMontofinalcalculado = Montofinalcalculado - Monto

        else:  # ingreso de efectivo
            logging.info('Ingreso al ELSE')
            NuevoMontofinalcalculado = Montofinalcalculado + Monto

        MontoTotalCalculado = NuevoMontofinalcalculado + Comisionbanco

        actualizarMontoComisionCaja(NuevoMontofinalcalculado, Comisionbanco, MontoTotalCalculado, CajaId)

        logging.info('---------------------Fin de actualizarEfectivoCaja---------------------')
    except Exception as ex:
        logging.info('actualizarEfectivoCaja - error: ' + str(ex))
        raise Exception(ex)


def ajustaCajaEfectivo (Monto, Comision, TipoOperacionId, BancoId, Comisionbancoid, cajaSolesId, comentario):
    try:
        logging.info('---------------------Inicio de ajustaCajaEfectivo---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        Fecha = str(obtenerFechaActual())

        if int(Comisionbancoid) == 2: #comision ingreso en 2:banco 1:efectico
            logging.info('Ingreso al IF')
            ComisionBanco = Comision
            ComisionEfectivo =0
        else:
            logging.info('Ingreso al ELSE')
            ComisionBanco = 0
            ComisionEfectivo = Comision

        #rollback del banco
        #if (int(BancoId) != 15 and int(BancoId) != 17):
        logging.info('Ingreso al IF')
        Select = "SELECT cajaid, bancoid, montoinicial, montofinalreal, fecha, montofinalcalculado, estado, comisionbanco  from caja"
        Select = Select + " where estado isnull and fecha= '" + Fecha + "'" + " and bancoid=" + str(BancoId)
        cur.execute(Select)
        caja = cur.fetchall()

        CajaId = caja[0][0]
        Montoinicial = caja[0][2]
        Montofinalcalculado = caja[0][5]
        ComisionBancoS = caja[0][7]
        logging.info('ComisionBancoS: ' + str(ComisionBancoS))
        ComisionBancoS = float(ComisionBancoS) - float(ComisionBanco)
        logging.info('Montoinicial: ' + str(Montoinicial))
        logging.info('Montofinalcalculado: ' + str(Montofinalcalculado))

        if int(TipoOperacionId) == 1:  # salida de efectivo
           logging.info('Ingreso al IF')
           NuevoMontofinalcalculadoBanco = Montofinalcalculado - float(Monto)
        else:  # ingreso de efectivo
           logging.info('Ingreso al ELSE')
           NuevoMontofinalcalculadoBanco = Montofinalcalculado + float(Monto)

        Montototalcalculado = NuevoMontofinalcalculadoBanco + ComisionBancoS

        actualizarMontoComisionCaja(NuevoMontofinalcalculadoBanco, ComisionBancoS,
                                        Montototalcalculado, CajaId)


        # Si no es una operacion Wester Remesa, se actualiza la caja de EFECTIVO - AGENTE
        #if (int(BancoId) != 15 and int(BancoId) != 17):
        #logging.info('Ingreso al IF')

            #if session['rolid'] == 2:
            #    logging.info('Ingreso al SUB IF')
            #    BancoIdCajaEfectivo = 19  # caja secundario
            #else:
            #    logging.info('Ingreso al SUB ELSE')
            #    BancoIdCajaEfectivo = 7  # caja principal

        # Si es una operacion de WESTER Remesa, se actualiza la caja de Wester Remesa.
        #else:
        #    logging.info('Ingreso al ELSE')
        #    BancoIdCajaEfectivo = BancoId

        # rollback del efectivo
        if "COMISION:" in comentario:
            logging.info('Al ser un registro de un pago de una COMISION, no se realiza rollback en la caja de EFECTIVO')
        else:
            BancoIdCajaEfectivo = cajaSolesId
            Select = "SELECT cajaid, bancoid, montoinicial, montofinalreal, fecha, montofinalcalculado, estado, comisionbanco  from caja"
            Select = Select + " where estado isnull and fecha= '" + Fecha + "'" + " and bancoid="+str(BancoIdCajaEfectivo)
            cur.execute(Select)
            caja = cur.fetchall()
            CajaId = caja[0][0]
            Montofinalcalculado = caja[0][5]
            ComisionBancoEfectivo = caja[0][7]
            logging.info('Montofinalcalculado: ' + str(Montofinalcalculado))
            logging.info('ComisionBancoEfectivo: ' + str(ComisionBancoEfectivo))
            logging.info('ComisionEfectivo: ' + str(ComisionEfectivo))
            ComisionBancoEfectivo = float(ComisionBancoEfectivo) - float(ComisionEfectivo)

            if int(TipoOperacionId) == 1:  # salida de efectivo
                logging.info('Ingreso al IF')
                NuevoMontofinalCalculadoEfectivo = Montofinalcalculado + float(Monto)

            else:  # ingreso de efectivo
                logging.info('Ingreso al ELSE')
                NuevoMontofinalCalculadoEfectivo = Montofinalcalculado - float(Monto)

            MontototalcalculadoEfectivo = NuevoMontofinalCalculadoEfectivo + ComisionBancoEfectivo
            actualizarMontoComisionCaja(NuevoMontofinalCalculadoEfectivo, ComisionBancoEfectivo, MontototalcalculadoEfectivo, CajaId)

        logging.info('---------------------Fin de ajustaCajaEfectivo---------------------')
    except Exception as ex:
        logging.info('ajustaCajaEfectivo - error: ' + str(ex))
        raise Exception(ex)


def obtenerCapital():
    logging.info('---------------------Inicio de obtenerCapital---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    Select = "SELECT sum(monto) from capital  where tipo like  'EFECTIVO%'"
    cur.execute(Select)
    list_capital = cur.fetchall()
    logging.info('Fin de obtenerCapital')
    return list_capital


def actualizarCajaDolar(TipoOperacionId, BancoId, Monto, TipoCambio, TipoMonedaId, esRegistro):
    try:
        logging.info('---------------------Inicio de actualizarCajaDolar---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        Fecha = str(obtenerFechaActual())
        Select = "SELECT cajaid, bancoid, montoinicial, montofinalreal, fecha, montofinalcalculado, estado, montodolarsolcalculado  from caja"
        Select = Select + " where estado isnull and fecha= '" + Fecha + "'" + " and bancoid=" + str(BancoId)
        cur.execute(Select)
        caja = cur.fetchall()

        CajaId = caja[0][0]
        Montoinicial = caja[0][2]
        Montofinalcalculado = caja[0][5]
        Montodolarsolcalculado = caja[0][7]
        logging.info('Monto: ' + str(Monto))
        logging.info('Montofinalcalculado: ' + str(Montofinalcalculado))
        logging.info('TipoCambio: ' + str(TipoCambio))
        if esRegistro: #registro
            logging.info('Ingreso al IF')
            if int(TipoOperacionId) == 1:  #salida de efectivo
                logging.info('Ingreso al SUB IF')
                NuevoMontofinalcalculadoBanco = Decimal(Montofinalcalculado) + Decimal(Monto)
            else: #ingreso de efectivo
                logging.info('Ingreso al SUB ELSE')
                NuevoMontofinalcalculadoBanco = Decimal(Montofinalcalculado) - (Decimal(Monto)/Decimal(TipoCambio))
        else: #eliminar
            logging.info('Ingreso al ELSE')
            if int(TipoOperacionId) == 1:  #salida de efectivo
                logging.info('Ingreso al SUB IF')
                NuevoMontofinalcalculadoBanco = Decimal(Montofinalcalculado) - Decimal(Monto)
            else: #ingreso de efectivo
                logging.info('Ingreso al SUB ELSE')
                NuevoMontofinalcalculadoBanco = Decimal(Montofinalcalculado) + (Decimal(Monto)/Decimal(TipoCambio))

        #Se calcula el monto de $ convertidos en s./ con un tipo de cambio referencial.
        valorCompraVirtual, valorVentaVirtual = consultarTipoCambioReferencia()
        NuevoMontodolarsolcalculado = round((Decimal(NuevoMontofinalcalculadoBanco) * Decimal(valorVentaVirtual)), 1)

        NuevoMontofinalcalculadoBanco = round(NuevoMontofinalcalculadoBanco, 3)
        logging.info('valorCompraVirtual: ' + str(valorCompraVirtual))
        logging.info('valorVentaVirtual: ' + str(valorVentaVirtual))
        logging.info('NuevoMontofinalcalculadoBanco: ' + str(NuevoMontofinalcalculadoBanco))
        logging.info('NuevoMontodolarsolcalculado: ' + str(NuevoMontodolarsolcalculado))
        logging.info('CajaId: ' + str(CajaId))

        Update = "UPDATE caja SET montofinalcalculado=%s, montototalcalculado=%s, montodolarsolcalculado=%s where cajaid=%s"
        cur.execute(Update, (NuevoMontofinalcalculadoBanco, NuevoMontofinalcalculadoBanco, NuevoMontodolarsolcalculado, CajaId))
        conn.commit()

        actualizarEfectivoCajaDolar(Monto, TipoCambio, TipoOperacionId,esRegistro)
        logging.info('---------------------Fin de actualizarCajaDolar---------------------')
        return NuevoMontofinalcalculadoBanco
    except Exception as ex:
        logging.info('actualizarCajaDolar - error: ' + str(ex))
        raise Exception(ex)


def actualizarEfectivoCajaDolar (Monto, TipoCambio, TipoOperacionId, esRegistro):
    try:
        logging.info('---------------------Inicio de actualizarEfectivoCajaDolar---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        bancoIdCajaEfectivo = session['cajaSolesId']
        Fecha = str(obtenerFechaActual())
        Select = "SELECT cajaid, bancoid, montoinicial, montofinalreal, fecha, montofinalcalculado, estado, comisionbanco  from caja"
        Select = Select + " where estado isnull and fecha= '" + Fecha + "'" + " and bancoid=" + str(bancoIdCajaEfectivo)
        cur.execute(Select)
        caja = cur.fetchall()
        CajaId = caja[0][0]
        Montoinicial = caja[0][2]
        Montofinalcalculado = caja[0][5]
        Comisionbanco = caja[0][7]

        logging.info('CajaId: ' + str(CajaId))
        logging.info('Montoinicial: ' + str(Montoinicial))
        logging.info('Montofinalcalculado: ' + str(Montofinalcalculado))
        logging.info('Monto: ' + str(Monto))
        logging.info('TipoCambio: ' + str(TipoCambio))

        if esRegistro:  # registro
            logging.info('Ingreso al IF')
            if int(TipoOperacionId) == 1:  # salida de efectivo
                logging.info('Ingreso al SUB IF')
                NuevoMontofinalcalculado = Decimal(Montofinalcalculado) - (Decimal(Monto)*Decimal(TipoCambio))
            else:  # ingreso de efectivo
                logging.info('Ingreso al SUB ELSE')
                NuevoMontofinalcalculado = Decimal(Montofinalcalculado) + Decimal(Monto)
        else:  # eliminar
            logging.info('Ingreso al ELSE')
            if int(TipoOperacionId) == 1:  # salida de efectivo
                logging.info('Ingreso al SUB IF')
                NuevoMontofinalcalculado = Decimal(Montofinalcalculado) + (Decimal(Monto)*Decimal(TipoCambio))
            else:  # ingreso de efectivo
                logging.info('Ingreso al SUB ELSE')
                NuevoMontofinalcalculado = Decimal(Montofinalcalculado) - Decimal(Monto)

        NuevoMontofinalcalculado = round(NuevoMontofinalcalculado, 3)
        Montototalcalculado = NuevoMontofinalcalculado +  Decimal(Comisionbanco)
        Update = "UPDATE caja SET montofinalcalculado=%s, montototalcalculado=%s where cajaid=%s"
        cur.execute(Update, (NuevoMontofinalcalculado, Montototalcalculado, CajaId))
        conn.commit()
        logging.info('NuevoMontofinalcalculado: ' + str(NuevoMontofinalcalculado))
        logging.info('---------------------Fin de actualizarEfectivoCajaDolar---------------------')
    except Exception as ex:
        logging.info('Error - NuevoMontofinalcalculado : ' + str(ex))
        raise Exception(ex)


def listarCaja():
    logging.info('---------------------Inicio de listarCaja---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "select catalogo_id, codigo, nombre, descripcion, valor1, valor2 from catalogo where codigo ='ASIGNACION_CAJA'"
    cur.execute(sql)
    list = cur.fetchall()
    logging.info('Fin de listarCaja')
    return list


def asignacionCaja(catalogoId):
    logging.info('---------------------Inicio de asignacionCaja---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "select catalogo_id, codigo, nombre, descripcion, valor1, valor2 from catalogo where catalogo_id ={0}".format(catalogoId)
    cur.execute(sql)
    list = cur.fetchall()
    #asignacion de cajas agente
    session['cajaSolesId'] = list[0][4].split("|")[0]
    session['cajaDolaresId'] = list[0][5].split("|")[0]
    #asignacion de bancos de wu
    session['cajaSolesWuId'] = list[0][4].split("|")[1]
    session['cajaDolaresWuId'] = list[0][5].split("|")[1]

    session['cajaDescripcion'] = list[0][3]
    logging.info('Fin de asignacionCaja')
    return list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_required
def cargarImagen():
    logging.info('---------------------Inicio de cargarImagen---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        # obtenemos el archivo del input "archivo"
        for file in request.files:
            #f = request.files[file]
            nombreArchivo= file.split('|')[0]
            nombreBanco = file.split('|')[1]

            if request.files[file].filename!="" and allowed_file(request.files[file].filename):
                filename = secure_filename(request.files[file].filename)
                # Guardamos el archivo en el directorio "Archivos PDF"
                try:
                    request.files[file].save(os.path.join('static/uploads', nombreArchivo+".jpg"))
                    CajaId = int(nombreArchivo)
                    Url = "/static/uploads/"+nombreArchivo+".jpg"
                    Update = "UPDATE caja SET url=%s where cajaid=%s"
                    cur.execute(Update, (Url, CajaId))
                    conn.commit()
                    logging.info('CajaId: ' + str(CajaId))
                    logging.info('Url: ' + str(Url))
                    Path = "static/uploads/"+nombreArchivo+".jpg"
                    MontoFinalReal = obtenerNumero(Path, nombreBanco)
                    monto2 = obtenerTexto(Path, nombreBanco)
                    logging.info('monto: ' + str(MontoFinalReal))
                    #logging.info('monto2: ' + str(monto2))

                    #MontoFinalReal = monto
                    #CajaId = int(item)
                    if "IZIPAY" or "YAPE" in nombreBanco:
                        Modificado = datetime.now()
                        ModificadoPor = session['usuarioid']
                        MontoFinalReal=MontoFinalReal.replace(",", "")
                        actualizarCajaMontoFinalReal(MontoFinalReal, Modificado, ModificadoPor, CajaId)


                except Exception as ex:
                    logging.info('Error - cargarImagen : ' + str(ex))

        logging.info('---------------------Fin de cargarImagen---------------------')
        return redirect(url_for('cargarImagen'))

    else:
        fechaDeHoy = str(obtenerFechaActual())
        list_cajas = selectCaja(fechaDeHoy)
        logging.info('---------------------Fin de cargarImagen---------------------')
        return render_template('cajaCierreCaptura.html', list_cajas=list_cajas)
