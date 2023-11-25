from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import config
import psycopg2.extras
from decimal import Decimal
from flask_login import LoginManager, login_user, logout_user, login_required
from datetime import date, datetime, timedelta
from caja import actualizarCajaBanco, ajustaCajaEfectivo, actualizarCajaDolar
import os
from utilitario import obtenerFechaActual, obtenerFechaAnterior
import tipoCambio

@login_required
def nuevaOperacionWu():
    logging.info('---------------------Inicio de nuevaOperacionWu---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    queryTipoOperacion = "SELECT tipooperacionid, nombrewu FROM tipooperacion order by tipooperacionid"
    cur.execute(queryTipoOperacion)
    list_tipooperaciones = cur.fetchall()

    modalidadid = 1  # Compra Presencial
    valor_compra, valor_venta = tipoCambio.consultar(modalidadid)
    logging.info('---------------------Fin de nuevaOperacionWu---------------------')
    return render_template('wu/NuevaOperacion.html', list_tipooperaciones=list_tipooperaciones, valor_compra=valor_compra, valor_venta=valor_venta)

def validarAperturaCaja():
    conn = config.get_db_connection()
    Fecha = str(obtenerFechaActual())
    Select = "SELECT count(cajaid) from caja as ca left join banco ba on ba.bancoid =ca.bancoid where ba.eswu=1 and fecha= '" + Fecha + "'"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_caja = cur.fetchall()
    if int(list_caja[0][0]) == 0:
        logging.info('Ingreso al SUB IF')
        flash('No se tiene aperturada caja para la fecha:' + Fecha, 'error')
        return False
    return True

def nuevaOperacionWuSolDao(Operacionid, BancoId, TipoOperacionId, Montosolwu, Montosolcaja, Comision, Comentario):
    if TipoOperacionId==1: # Cuando es "Salida de Efectivo (RETIRO)" se coloca el signo negativo
        Montosolwu = Montosolwu*-1
        Montosolcaja = Montosolcaja*-1

    FechaOperacion = obtenerFechaActual()
    FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour,
                                                                                       minutes=datetime.now().minute,
                                                                                       seconds=datetime.now().second)



    TipoMonedaId = int(1) #Sol
    Saldo = 0
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "INSERT INTO operacionesWU ("
        "operacionid, "
        "tipooperacionid, "
        "montosolbanco, "
        "montosolcaja, "
        "comisionsol, "
        "fechaoperacion, "
        "comentario, "
        "tipomonedaid, "
        "bancoid, "
        "saldo, "
        "usuarioid, "
        "bancoefectivoid) "
        "VALUES "
        "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (Operacionid, TipoOperacionId, Montosolwu, Montosolcaja, Comision, FechaOperacion, Comentario, TipoMonedaId, BancoId, Saldo, session['usuarioid'], session['cajaSolesWuId']))
    conn.commit()
    logging.info('TipoOperacionId: ' + str(TipoOperacionId))
    logging.info('Montosolwu: ' + str(Montosolwu))
    logging.info('Montosolcaja: ' + str(Montosolcaja))
    logging.info('Comision: ' + str(Comision))
    logging.info('FechaOperacion: ' + str(FechaOperacion))
    logging.info('Comentario: ' + str(Comentario))
    logging.info('TipoMonedaId: ' + str(TipoMonedaId))
    logging.info('BancoId: ' + str(BancoId))
    logging.info('Saldo: ' + str(Saldo))
    logging.info('usuarioid: ' + str(session['usuarioid']))
    logging.info('bancoefectivoid: ' + str(session['cajaSolesWuId']))


@login_required
def nuevaOperacionWuSol():
    logging.info('---------------------Inicio de nuevaOperacionWuSol---------------------')
    if validarAperturaCaja()==False:
        return redirect(url_for('nuevaOperacionWu'))

    TipoOperacionId = int(request.form['tipoOperacionIdSol'])
    Comision = float(request.form['montoSolCaja'])
    Comentario = request.form['comentario']
    Montosolwu = float(request.form['montoSolWu'])
    BancoId = int(30)  # WESTER UNION - REMESA - SOLES

    BcpSol = request.form.getlist('bcpSol')
    Operacionid = obtenerOperacionId()
    Montosolcaja = Montosolwu
    flash('Operacion registrada con exito.' + " Monto:" + str(Montosolwu), 'success')
    if BcpSol:
        nuevaOperacionWuSolDao(Operacionid, 26, TipoOperacionId, Montosolwu, 0, 0, Comentario)
        Montosolcaja=0

    nuevaOperacionWuSolDao(Operacionid, BancoId, TipoOperacionId, Montosolwu, Montosolcaja, Comision, Comentario)


    logging.info('---------------------Fin de nuevaOperacionWuSol---------------------')
    return redirect(url_for('listaOperacion'))

def nuevaOperacionWuDolarDao(Operacionid, BancoId, TipoOperacionId, MontoDolarWu, ComisionSol, Comentario, MontoDolarCaja, MontoSolCaja, TipoCambioCompra, TipoCambioVenta, TipoMonedaId):
    Saldo = 0
    FechaOperacion = obtenerFechaActual()
    FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour,
                                                                                       minutes=datetime.now().minute,
                                                                                       seconds=datetime.now().second)

    if TipoOperacionId==1: # Cuando es "Salida de Efectivo (RETIRO)" se coloca el signo negativo
        MontoDolarWu = MontoDolarWu*-1
        MontoDolarCaja = MontoDolarCaja*-1
        MontoSolCaja = MontoSolCaja*-1


    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "INSERT INTO operacioneswu ("
        "operacionid, "
        "tipooperacionid, "
        "montodolarbanco, "
        "comisionsol, "
        "fechaoperacion, "
        "comentario, "
        "montodolarcaja, "
        "montosolcaja, "
        "tipocambiocompra, "
        "tipocambioventa, "
        "tipomonedaid, "
        "bancoid, "
        "saldo, "
        "usuarioid) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            Operacionid,
            TipoOperacionId,
            MontoDolarWu,
            ComisionSol,
            FechaOperacion,
            Comentario,
            str(MontoDolarCaja),
            MontoSolCaja,
            TipoCambioCompra,
            TipoCambioVenta,
            TipoMonedaId,
            BancoId,
            Saldo,
            str(session['usuarioid'])))
    conn.commit()
    logging.info('TipoOperacionId: ' + str(TipoOperacionId))
    logging.info('Montodolarbanco: ' + str(MontoDolarWu))
    logging.info('ComisionSol: ' + str(ComisionSol))
    logging.info('FechaOperacion: ' + str(FechaOperacion))
    logging.info('Comentario: ' + str(Comentario))
    logging.info('MontoDolarCaja: ' + str(MontoDolarCaja))
    logging.info('MontoSolCaja: ' + str(MontoSolCaja))
    logging.info('TipoCambioCompra: ' + str(TipoCambioCompra))
    logging.info('TipoCambioVenta: ' + str(TipoCambioVenta))
    logging.info('TipoMonedaId: ' + str(TipoMonedaId))
    logging.info('BancoId: ' + str(BancoId))
    logging.info('Saldo: ' + str(Saldo))
    logging.info('usuarioid: ' + str(session['usuarioid']))


@login_required
def nuevaOperacionWuDolar():
    logging.info('---------------------Inicio de nuevaOperacionWuDolar---------------------')
    if validarAperturaCaja() == False:
        return redirect(url_for('nuevaOperacionWu'))

    TipoOperacionId     = int(request.form['tipoOperacionIdDolar'])
    MontoDolarWu        = float(request.form['montoDolarWu'])
    ComisionSol         = float(request.form['comisionSol'])
    Comentario          = request.form['comentario']
    MontoDolarCaja      = float(request.form['montoDolarCaja'])
    MontoSolCaja        = float(request.form['montoSolCaja'])
    TipoCambioCompra    = float(request.form['tipoCambioCompra'])
    TipoCambioVenta     = float(request.form['tipoCambioVenta'])
    BancoId             = int(31)  # WESTER UNION - REMESA - DOLARES
    TipoMonedaId        = int(2)  # Dolar
    BcpDolar            = request.form.getlist('bcpDolar')
    BcpSol              = request.form.getlist('bcpSol')

    modalidadid = 1  # Compra Presencial
    tipoCambio.insertar(TipoCambioVenta, TipoCambioCompra, modalidadid);

    #### INCIIO DE VALIDACIONES #######
    if TipoOperacionId==1: #Salida de Efectivo (RETIRO)
        TipoCambioVenta = 0
        ValidarMontoCaja = TipoCambioCompra * (MontoDolarWu - MontoDolarCaja)

        if (round(ValidarMontoCaja,3) != MontoSolCaja): #validacion de datos
            logging.info('------------------------')
            flash('No se puedo registrar, favor de volver a intentar.' + " Monto:" + str(MontoDolarWu), 'Error')
            logging.info('---------------------Fin de nuevaOperacionWuDolar---------------------')
            return redirect(url_for('nuevaOperacionWu'))

    else: #Ingreso de Efectivo (ENVIO)

        if MontoDolarWu > MontoDolarCaja :
            ValidarMontoCaja    = TipoCambioVenta * (MontoDolarWu-MontoDolarCaja)
            TipoCambioCompra    = 0
        else:
            ValidarMontoCaja    = TipoCambioCompra * (MontoDolarWu - MontoDolarCaja)
            TipoCambioVenta     = 0

        if (round(ValidarMontoCaja,3) != MontoSolCaja): #validacion de datos
            logging.info('------------------------')
            flash('No se puedo registrar, favor de volver a intentar.' + " Monto:" + str(MontoDolarWu), 'Error')
            logging.info('---------------------Fin de nuevaOperacionWuDolar---------------------')
            return redirect(url_for('nuevaOperacionWu'))

    #### FIN DE VALIDACIONES #######


    Operacionid = obtenerOperacionId()

    if BcpDolar:
        # registro en 27=BCP - DOLARES
        MontoDolarBanco = MontoDolarCaja
        nuevaOperacionWuDolarDao(Operacionid, 27, TipoOperacionId, MontoDolarBanco, 0, Comentario, 0, 0, 0, 0, TipoMonedaId)
        MontoDolarCaja = 0

    if BcpSol:
        Montosolwu = MontoSolCaja
        #registro en 26=BCP - SOLES
        nuevaOperacionWuSolDao(Operacionid, 26, TipoOperacionId, Montosolwu, 0, 0, Comentario)
        MontoSolCaja = 0

    #registro en banco WU
    nuevaOperacionWuDolarDao(Operacionid, BancoId, TipoOperacionId, MontoDolarWu, ComisionSol, Comentario, MontoDolarCaja, MontoSolCaja,
                             TipoCambioCompra, TipoCambioVenta, TipoMonedaId)


    flash('Operacion registrada con exito.' + " Monto:" + str(MontoDolarWu), 'success')

    logging.info('---------------------Fin de nuevaOperacionWuDolar---------------------')
    return redirect(url_for('listaOperacion'))

@login_required
def listaOperacion():
    logging.info('---------------------Inicio de listaOperacion---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fechaActual = str(obtenerFechaActual())
    RecargaSaldo = False
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

        s = "SELECT " \
            "ROW_NUMBER () OVER(ORDER BY operacionid DESC) as indice, " \
            "b.nombre, " \
            "top.nombrewu, " \
            "op.operacionid, " \
            "op.montosolbanco, " \
            "op.comisionsol, " \
            "op.fechaoperacion, " \
            "op.comentario, " \
            "tm.nombre, " \
            "op.saldo, " \
            "top.tipooperacionid, " \
            "op.bancoid, " \
            "usu.nombre, " \
            "usu.usuarioid, " \
            "op.montodolarbanco, " \
            "op.montodolarcaja, " \
            "op.montosolcaja, "\
            "op.tipocambiocompra, " \
            "op.tipocambioventa, " \
            "op.montodolarbanco " \
            "FROM operacioneswu as op " \
            "left  join  tipomoneda tm on tm.tipomonedaid = op.tipomonedaid " \
            "left join tipooperacion top on top.tipooperacionid = op.tipooperacionid " \
            "left join banco b on b.bancoid =op.bancoid " \
            "left join usuario usu on usu.usuarioid =op.usuarioid "

        s = s + "where op.fechaoperacion between %s and  %s "
        #SelectSumaComision = "SELECT sum(comision), sum(numerooperacion) FROM operaciones where fechaoperacion between %s and  %s"
        if BancoId == '0':
            logging.info('BancoId es CERO')
        else:
            s = s + " and b.bancoid= " + str(BancoId)
            #SelectSumaComision = SelectSumaComision + " and bancoid=" + BancoId

        if TipoOperacionId == '0':
            logging.info('TipoOperacionId es CERO')
        else:
            s = s + " and op.tipooperacionid= " + str(TipoOperacionId)
            #SelectSumaComision = SelectSumaComision + " and tipooperacionid=" + TipoOperacionId

        if RecargaSaldo:
            s = s + " and op.comentario not like '%%RECARGA%%' "
        if soloMisOperaciones:
            s = s + " and op.usuarioid=" + str(session['usuarioid'])
            #SelectSumaComision = SelectSumaComision + " and usuarioid=" + str(session['usuarioid'])

        s = s + "order by op.operacionid DESC "
        try:
            cur.execute(s, (fechaInicio, fechaFin + " 23:59:59"))
        except Exception as ex:
            raise Exception(ex)

    else:
        fechaInicio = str(obtenerFechaActual())
        # fechaFin=(date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        fechaFin = fechaInicio

        s = "SELECT " \
            "ROW_NUMBER () OVER(ORDER BY operacionid DESC) as indice, " \
            "b.nombre, " \
            "top.nombrewu, " \
            "op.operacionid, " \
            "op.montosolbanco, " \
            "op.comisionsol, " \
            "op.fechaoperacion, " \
            "op.comentario, " \
            "tm.nombre, " \
            "op.saldo, " \
            "top.tipooperacionid, " \
            "op.bancoid, " \
            "usu.nombre, " \
            "usu.usuarioid, " \
            "op.montodolarbanco, " \
            "op.montodolarcaja, " \
            "op.montosolcaja, "\
            "op.tipocambiocompra, " \
            "op.tipocambioventa, " \
            "op.montodolarbanco " \
            "FROM operacioneswu as op " \
            "left  join  tipomoneda tm on tm.tipomonedaid = op.tipomonedaid " \
            "left join tipooperacion top on top.tipooperacionid = op.tipooperacionid " \
            "left join banco b on b.bancoid =op.bancoid " \
            "left join usuario usu on usu.usuarioid =op.usuarioid "

        s = s + "where op.fechaoperacion between %s and  %s "
        #s = s + " and op.comentario not like '%%RECARGA%%' "
        #s = s + " and b.bancoid=15 "
        #SelectSumaComision = "SELECT sum(comision), sum(numerooperacion) FROM operaciones where fechaoperacion between %s and  %s"

        #if soloMisOperaciones:
        #    s = s + " and op.usuarioid=" + str(session['usuarioid'])
        #    SelectSumaComision = SelectSumaComision + " and usuarioid=" + str(session['usuarioid'])

        s = s + " order by op.operacionid DESC "
        try:
            cur.execute(s, (fechaInicio, fechaFin + " 23:59:59"))
        except Exception as ex:
            raise Exception(ex)
        BancoId = '0'
        TipoOperacionId = '0'

    list_operaciones = cur.fetchall()
    scriptBanco = "SELECT bancoid, nombre FROM banco where eswu = 1 and bancoid not in (22, 23, 32, 33, 34, 35, 36, 37, 38, 39) order by bancoid"
    cur.execute(scriptBanco)
    list_banco = cur.fetchall()

    list_banco.insert(0, [0, "TODOS"])
    list_banco.insert(1, [23, "COMPRA/VENTA $"])

    scriptTipoOperacion = "SELECT tipooperacionid, nombrewu FROM tipooperacion order by tipooperacionid"
    cur.execute(scriptTipoOperacion)  # Execute the SQL
    list_tipooperaciones = cur.fetchall()
    list_tipooperaciones.insert(0, [0, "TODOS"])

    #cur.execute(SelectSumaComision, (fechaInicio, fechaFin + " 23:59:59"))
    #sumaComision = cur.fetchall()

    logging.info('---------------------Fin de listaOperacion---------------------')
    return render_template('wu/ListaOperacion.html',
                           list_operaciones=list_operaciones,
                           list_banco=list_banco,
                           fechaInicio=fechaInicio, fechaFin=fechaFin,
                           bancoSelectedId=BancoId,
                           tipoOperacionSelectedId=TipoOperacionId,
                           fechaActual=fechaActual,
                           list_tipooperaciones=list_tipooperaciones,
                           recargaSaldo=RecargaSaldo,
                           soloMisOperaciones=soloMisOperaciones)

@login_required
def eliminar(id):
    logging.info('---------------------Inicio de eliminar---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #Select = "SELECT usuarioid from operacioneswu where operacionid= '" + id + "'"
    #cur.execute(Select)
    #list_operacion = cur.fetchall()
    #usuarioid = list_operacion[0][0]

    cur.execute('DELETE FROM operacioneswu WHERE operacionid = {0}'.format(id))
    conn.commit()
    logging.info('id: ' + str(id))
    flash('Operacion eliminada con exito. ','success')
    logging.info('---------------------Fin de eliminar---------------------')
    return redirect(url_for('listaOperacion'))

@login_required
def transferirWu():
    logging.info('---------------------Inicio de transferir---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        logging.info('Ingreso al IF')
        if validarAperturaCaja() == False:
            return redirect(url_for('transferirWu'))

        Monto = float(request.form['monto'])
        BancoDestinoId = int(request.form['BancoDestinoId'])
        BancoOrigenId = int(request.form['BancoOrigenId'])
        TipoOperacionId = 2  # Ingreso de Efectivo (DEPOSITO)
        ComisionSol = 0
        Comentario = request.form['comentario']
        Operacionid = obtenerOperacionId()
        if (BancoDestinoId==22): #EFECTIVO WU (Caja Principal) - SOLES
            Montosolwu = Monto*-1
            Montosolcaja = Monto
            nuevaOperacionWuSolDao(Operacionid, BancoOrigenId, TipoOperacionId, Montosolwu, Montosolcaja , ComisionSol, Comentario)
        else:

            MontoDolarCaja=Monto
            MontoDolarWu = Monto * -1
            MontoSolCaja=0
            TipoCambioCompra=0
            TipoCambioVenta=0
            TipoMonedaId = int(2)  # Dolar


            nuevaOperacionWuDolarDao(Operacionid, BancoOrigenId, TipoOperacionId, MontoDolarWu, ComisionSol, Comentario, MontoDolarCaja,
                                     MontoSolCaja,
                                     TipoCambioCompra, TipoCambioVenta, TipoMonedaId)


        flash('Transferencia registrada con exito. ' + 'Monto: '+str(Monto) ,'success')
        logging.info('---------------------Fin de transferir---------------------')
        return redirect(url_for('transferirWu'))
    else:
        logging.info('Ingreso al ELSE')
        sBanco = "SELECT bancoid, nombre FROM banco where eswu=1 and  nombre like '%BCP%' order by orden"
        cur.execute(sBanco)  # Execute the SQL
        list_banco_origen = cur.fetchall()

        sBanco = "SELECT bancoid, nombre FROM banco where eswu=1 and  nombre like '%Principal%' order by orden"
        cur.execute(sBanco)  # Execute the SQL
        list_banco_destino = cur.fetchall()

        logging.info('---------------------Fin de transferir---------------------')
        return render_template('wu/Transferir.html', list_banco_origen=list_banco_origen, list_banco_destino=list_banco_destino)

@login_required
def compraventadolarWu():
    logging.info('---------------------Inicio de compraventadolarWu---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    modalidadid=1 #Compra Presencial

    if request.method == 'POST':
        logging.info('Ingreso al IF')
        Fecha = str(obtenerFechaActual())
        if validarAperturaCaja() == False:
            return redirect(url_for('compraventadolarWu'))

        montoEnviar = request.form['enviar']
        montoRecibir = request.form['recibir']
        tipoMonedaEnviar = ""
        tipoMonedaRecibir = ""
        valor_compra = request.form['valor_compra']
        valor_venta = request.form['valor_venta']

        if float(valor_compra) < 1:
            flash('No se tiene registrado el tipo de Compra.', 'error')
            return redirect(url_for('compraventadolar'))

        if float(valor_venta) < 1:
            flash('No se tiene registrado el tipo de Venta.', 'error')
            return redirect(url_for('compraventadolar'))

        cambioValor = request.form['cambioValor']
        descripcion = request.form['Descripcion']

        if cambioValor=="Soles":
            logging.info('Ingreso al SUB 3 IF')
            TipoOperacionId = 2  # Ingreso de efecto S./ por que se vende dolares e ingresa soles.
            tipoCambioValor = valor_venta
            TipoMonedaId = 1 # Tipo de Moneda que ingresa S/
            textoValor = "VENTA : "
            tipoMonedaEnviar = "SOLES "
            tipoMonedaRecibir = "DOLARES "
        else:
            logging.info('Ingreso al SUB 3 ELSE')
            TipoOperacionId = 1  # Retiro de efectivo S./  por que se compra dolares
            tipoCambioValor = valor_compra
            TipoMonedaId= 2 # Tipo de Moneda que ingresa $
            textoValor = "COMPRA : "
            tipoMonedaEnviar = "$ "
            tipoMonedaRecibir = "SOLES "

        if int(TipoOperacionId) == 1:  # salida de efectivo
            logging.info('Ingreso al SUB IF')
            MontoDolarCaja = float(montoEnviar)*-1
            MontoSolCaja = round((Decimal(montoEnviar) * Decimal(tipoCambioValor)),2)
        else:  # ingreso de efectivo
            logging.info('Ingreso al SUB ELSE')
            MontoSolCaja = float(montoEnviar)
            MontoDolarCaja = round((Decimal(montoEnviar) *-1 / Decimal(tipoCambioValor)),2)

        Comentario = textoValor + str(tipoCambioValor) +"|"+ "comentario:" + descripcion

        MontoDolarWu        = 0
        ComisionSol         = 0
        TipoCambioCompra    = valor_compra
        TipoCambioVenta     = valor_venta
        BancoId             = 23  # WESTER UNION - REMESA - DOLARES


        Operacionid = obtenerOperacionId()

        nuevaOperacionWuDolarDao(
                                 Operacionid,
                                 BancoId,
                                 TipoOperacionId,
                                 MontoDolarWu,
                                 ComisionSol,
                                 Comentario,
                                 MontoDolarCaja,
                                 MontoSolCaja,
                                 TipoCambioCompra,
                                 TipoCambioVenta,
                                 TipoMonedaId
                                 )

        flash('Transferencia registrada con exito.' + ' Moneda:' + str(cambioValor) + ' Tipo de Cambio:' + str(tipoCambioValor) + ' Monto:' + str(montoEnviar),'success')
        tipoCambio.insertar(valor_venta, valor_compra, modalidadid)
        logging.info('---------------------Fin de compraventadolarWu---------------------')
        operacionid = 0
        return render_template(
                               'wu/CompraVentaDolar.html',
                               valor_venta=valor_venta,
                               valor_compra=valor_compra,
                               operacionid=operacionid,
                               tipoCambioValor=textoValor + str(tipoCambioValor),
                               montoEnviar=montoEnviar,
                               montoRecibir=montoRecibir,
                               tipoMonedaEnviar=tipoMonedaEnviar,
                               tipoMonedaRecibir=tipoMonedaRecibir,
                               Fecha=Fecha
                               )
    else:
        logging.info('Ingreso al ELSE')
        valor_compra, valor_venta = tipoCambio.consultar(modalidadid)
        logging.info('---------------------Fin de compraventadolar---------------------')
        return render_template('wu/CompraVentaDolar.html', valor_venta=valor_venta, valor_compra=valor_compra)

def obtenerOperacionId ():
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("select nextval('opreacionwu_sq');")
    list = cur.fetchall()
    Operacionid = list[0][0]
    return Operacionid
