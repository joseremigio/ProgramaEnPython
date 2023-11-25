from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import config
import psycopg2.extras
from flask_login import LoginManager, login_user, logout_user, login_required
from datetime import date, datetime, timedelta
from caja import actualizarCajaBanco, ajustaCajaEfectivo, actualizarCajaDolar, validarAperturaCaja, actualizarEfectivoCaja
import os
from utilitario import obtenerFechaActual, obtenerFechaAnterior
import tipoCambio

@login_required
def nuevaOperacion():
    logging.info('---------------------Inicio de nuevaOperacion---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        logging.info('Ingreso al IF')

        if validarAperturaCaja() == False:
            return redirect(url_for('nuevaOperacion'))

        validarPrimeraOperacion()

        if request.method == 'POST':
                logging.info('Ingreso al SUB SUB IF')
                TipoOperacionId = int(request.form['TipoOperacionId'])
                TipoMonedaId = int(1) #1:Sol
                MontoEfectivo = 0
                MontoBanco = 0
                Comision = 0
                try:
                    MontoEfectivo = float(request.form['MontoEfectivo'])
                    MontoBanco = float(request.form['MontoBanco'])
                    MontoTotal = MontoEfectivo + MontoBanco
                    Comision = float(request.form['Comision'])
                finally:
                    Comision = Comision

                FechaOperacion = obtenerFechaActual()
                FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)

                Comentario = "Comentario:"+ str(request.form['Comentario']) + "|Caja Descripcion:" + str(session['cajaDescripcion']) + "|CajaSolesId:" + str(session['cajaSolesId']) + "|CajaDolaresId:" + str(session['cajaDolaresId'])
                numerooperacion = request.form['numerooperacion']

                #ComisionBancoId = int(request.form['ComisionBanco'])
                BancoId = int(request.form['BancoId'])
                ComisionBanco = int(request.form['ComisionBanco'])

                Saldo = actualizarCajaBanco(TipoOperacionId, BancoId, MontoTotal, Comision, TipoMonedaId, ComisionBanco)

                ComisionEfectivo = 0
                if int(ComisionBanco) == 2:  # comision ingreso en 2:banco 1:efectico
                    ComisionEfectivo = 0
                else:
                    ComisionEfectivo = Comision

                actualizarEfectivoCaja(MontoTotal, ComisionEfectivo, TipoOperacionId)

                bancoNombreYtipoOperacionNombre = request.form['bancoNombreYtipoOperacionNombre']

                insertarOperacion(
                                        TipoOperacionId,
                                        MontoTotal,
                                        Comision,
                                        FechaOperacion,
                                        Comentario,
                                        TipoMonedaId,
                                        BancoId,
                                        Saldo,
                                        session['usuarioid'],
                                        numerooperacion,
                                        ComisionBanco
                                )

                # actualziar banco con el que se pago la operacion
                if MontoBanco>0:
                    PagoBancoId = int(request.form['PagoBancoId'])
                    TipoOperacionId = 1 #Salida de efectivo
                    Comision = 0
                    ComisionBanco = 1
                    #numerooperacion = 0
                    Comentario = "Comentario:" + "Pago por APP" + "|Caja Descripcion:" + str(
                        session['cajaDescripcion']) + "|CajaSolesId:" + str(
                        session['cajaSolesId']) + "|CajaDolaresId:" + str(session['cajaDolaresId'])

                    SaldoBancoPago = actualizarCajaBanco(TipoOperacionId, PagoBancoId, MontoBanco, Comision, TipoMonedaId,
                                                ComisionBanco)

                    actualizarEfectivoCaja(MontoBanco, Comision, TipoOperacionId)

                    insertarOperacion(
                                        TipoOperacionId,
                                        MontoBanco,
                                        Comision,
                                        FechaOperacion,
                                        Comentario,
                                        TipoMonedaId,
                                        PagoBancoId,
                                        SaldoBancoPago,
                                        session['usuarioid'],
                                        numerooperacion,
                                        ComisionBanco
                                    )

                flash('Operacion registrada con exito.' + 'Operacion: ' + bancoNombreYtipoOperacionNombre + " Monto:" +
                      str(MontoTotal) + ", Comision:" + request.form['Comision'], 'success')
                logging.info('---------------------Fin de nuevaOperacion---------------------')
                return redirect(url_for('home'))
    else:
        logging.info('Ingreso al ELSE')
        s = "SELECT tipooperacionid, nombre FROM tipooperacion order by tipooperacionid"
        cur.execute(s)  # Execute the SQL
        list_tipooperaciones = cur.fetchall()
        list_tipooperaciones.insert(2, [2, "Pago de Servicio (DEPOSITO)"])
        sBanco = "SELECT bancoid, nombre, estilocss FROM banco where eswu=0 and nombre NOT LIKE '%EFECTIVO%' order  by orden"
        cur.execute(sBanco)  # Execute the SQL
        list_banco= cur.fetchall()
        #conn.close()  # cierre de conexion
        logging.info('---------------------Fin de nuevaOperacion---------------------')
        return render_template('operacion.html', list_tipooperaciones=list_tipooperaciones, list_banco=list_banco)


def insertarOperacion (TipoOperacionId, Monto, Comision, FechaOperacion, Comentario, TipoMonedaId, BancoId, Saldo,
                     Usuarioid, numerooperacion, ComisionBanco):
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO operaciones (operacionid, tipooperacionid, monto, comision, fechaoperacion, comentario, tipomonedaid, bancoid, saldo, usuarioid, numerooperacion, comisionbancoid) VALUES (nextval('opreaciones_sq'),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    TipoOperacionId,
                    Monto,
                    Comision,
                    FechaOperacion,
                    Comentario,
                    TipoMonedaId,
                    BancoId, Saldo,
                    Usuarioid,
                    numerooperacion,
                    ComisionBanco
                )
    )
    conn.commit()
    logging.info('TipoOperacionId: ' + str(TipoOperacionId))
    logging.info('Monto: ' + str(Monto))
    logging.info('Comision: ' + str(Comision))
    logging.info('FechaOperacion: ' + str(FechaOperacion))
    logging.info('Comentario: ' + str(Comentario))
    logging.info('TipoMonedaId: ' + str(TipoMonedaId))
    logging.info('BancoId: ' + str(BancoId))
    logging.info('Saldo: ' + str(Saldo))
    logging.info('usuarioid: ' + str(session['usuarioid']))
    logging.info('numerooperacion: ' + str(numerooperacion))
    logging.info('ComisionBanco: ' + str(ComisionBanco))


@login_required
def delete_operacion(id, monto, comision, tipoOperacionId, bancoId, comisionbancoid):
    logging.info('---------------------Inicio de delete_operacion---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    Select = "SELECT tipocambio, tipooperacionid, bancoid, tipomonedaid , comentario from operaciones where operacionid= '" + id + "'"
    cur.execute(Select)
    list_operacion = cur.fetchall()
    comentario = list_operacion[0][4]
    list_comentario = comentario.split("|")[2].split(":")  # Se captura el ID de la caja de soles
    cajaSolesId = list_comentario[1]  # se obtiene el id de la caja en s./ cajaSolesId

    if (str(cajaSolesId)!=str(session['cajaSolesId'])):
         flash('Cambia de Caja Asiganda para eliminar esta Operación.', 'error')
         return redirect(url_for('home'))
    else:
        logging.info('Ingreso al ELSE')

    if ( "TRANSFERENCIA" in  comentario):
        flash('Una transferencia entre BANCOS no es posible eliminar, llamar a administrador.', 'error')
        return redirect(url_for('home'))
    else:
        logging.info('Ingreso al ELSE')

    if (bancoId=='16'  or bancoId=='18'): #rollbackCompraVentaDolar
        logging.info('Ingreso al IF')
        #Select = "SELECT tipocambio, tipooperacionid, bancoid, tipomonedaid from operaciones where operacionid= '" + id + "'"
        #cur.execute(Select)
        #list_operacion = cur.fetchall()
        tipoCambioValor = list_operacion[0][0]
        tipooperacionid = list_operacion[0][1]
        bancoDestinoId = list_operacion[0][2]
        tipoMonedaId = list_operacion[0][3]
        esRegistro = False
        logging.info('tipoCambioValor: ' + str(tipoCambioValor))
        logging.info('tipooperacionid: ' + str(tipooperacionid))
        logging.info('bancoDestinoId: ' + str(bancoDestinoId))
        logging.info('tipoMonedaId: ' + str(tipoMonedaId))
        logging.info('esRegistro: ' + str(esRegistro))
        saldo = actualizarCajaDolar(tipooperacionid, bancoDestinoId, monto, tipoCambioValor, tipoMonedaId, esRegistro)
        logging.info('saldo: ' + str(saldo))
    else:
        logging.info('Ingreso al ELSE')
        ajustaCajaEfectivo(monto, comision, tipoOperacionId, bancoId, comisionbancoid, cajaSolesId, comentario)

    cur.execute('UPDATE operaciones SET  estado= B' + "'1'"+' WHERE operacionid = {0}'.format(id))
    conn.commit()
    logging.info('id: ' + str(id))
    flash('Operacion eliminada con exito. '+'Monto: '+ monto + ', Id:' + id,'success')
    logging.info('---------------------Fin de delete_operacion---------------------')
    return redirect(url_for('home'))

@login_required
def transferir():
    logging.info('---------------------Inicio de transferir---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        logging.info('Ingreso al IF')
        if validarAperturaCaja() == False:
            return redirect(url_for('transferir'))

        Monto = float(request.form['Monto'])
        FechaOperacion = obtenerFechaActual()
        FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour,
                                                                                           minutes=datetime.now().minute,
                                                                                           seconds=datetime.now().second)

        #Comentario = "RECARGA SALDO"
        Comentario = "comentario:RECARGA SALDO (TRANSFERENCIA)"+ "|cajaDescripcion:" + str(
            session['cajaDescripcion']) + "|cajaSolesId:" + str(session['cajaSolesId']) + "|cajaDolaresId:" + str(
            session['cajaDolaresId'])

        TipoMonedaId = int(request.form['TipoMoneda'])
        BancoOrigenId = int(request.form['BancoOrigenId'])
        BancoDestinoId = int(request.form['BancoDestinoId'])
        TipoOperacionId = 2
        Saldo = actualizarCajaBanco(TipoOperacionId, BancoOrigenId, Monto, 0, TipoMonedaId, 0)
        actualizarEfectivoCaja(Monto, 0, TipoOperacionId)
        modalidadid = 1  # Compra Presencial
        valor_compra, valor_venta = tipoCambio.consultar(modalidadid)

        cur.execute(
            "INSERT INTO operaciones (operacionid, tipooperacionid, monto, comision, fechaoperacion, comentario, tipomonedaid, bancoid, saldo, usuarioid, numerooperacion, comisionbancoid, tipocambio) VALUES (nextval('opreaciones_sq'),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (2, Monto, 0, FechaOperacion, Comentario, TipoMonedaId, BancoOrigenId, Saldo, session['usuarioid'], 0, 1, valor_compra))
        conn.commit()
        logging.info('Monto: ' + str(Monto))
        logging.info('FechaOperacion: ' + str(FechaOperacion))
        logging.info('Comentario: ' + str(Comentario))
        logging.info('TipoMonedaId: ' + str(TipoMonedaId))
        logging.info('BancoOrigenId: ' + str(BancoOrigenId))
        logging.info('Saldo: ' + str(Saldo))
        logging.info('usuarioid: ' + str(session['usuarioid']))

        TipoOperacionId = 1
        Saldo = actualizarCajaBanco(TipoOperacionId, BancoDestinoId, Monto, 0, TipoMonedaId, 0)
        actualizarEfectivoCaja(Monto, 0, TipoOperacionId)

        cur.execute(
            "INSERT INTO operaciones (operacionid, tipooperacionid, monto, comision, fechaoperacion, comentario, tipomonedaid, bancoid, saldo, usuarioid, numerooperacion, comisionbancoid, tipocambio) VALUES (nextval('opreaciones_sq'),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (1, Monto, 0, FechaOperacion, Comentario, TipoMonedaId, BancoDestinoId, Saldo, session['usuarioid'], 0, 1, valor_compra))
        conn.commit()

        logging.info('Monto: ' + str(Monto))
        logging.info('FechaOperacion: ' + str(FechaOperacion))
        logging.info('Comentario: ' + str(Comentario))
        logging.info('TipoMonedaId: ' + str(TipoMonedaId))
        logging.info('BancoDestinoId: ' + str(BancoDestinoId))
        logging.info('Saldo: ' + str(Saldo))
        logging.info('usuarioid: ' + str(session['usuarioid']))

        flash('Transferencia registrada con exito. ' + 'Monto: '+str(Monto) ,'success')
        logging.info('---------------------Fin de transferir---------------------')
        return redirect(url_for('transferir'))
    else:
        logging.info('Ingreso al ELSE')
        sBanco = "SELECT bancoid, nombre FROM banco where eswu=0 order by orden"
        cur.execute(sBanco)  # Execute the SQL
        list_banco= cur.fetchall()
        #conn.close()  # cierre de conexion
        logging.info('---------------------Fin de transferir---------------------')
        return render_template('transferir.html', list_banco=list_banco)

@login_required
def compraventadolar():
    logging.info('---------------------Inicio de compraventadolar---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    modalidadid=1 #Compra Presencial

    if request.method == 'POST':
        logging.info('Ingreso al IF')
        Fecha = str(obtenerFechaActual())

        if validarAperturaCaja() == False:
            return redirect(url_for('compraventadolar'))

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

        FechaOperacion = obtenerFechaActual()
        FechaOperacion = datetime.combine(FechaOperacion, datetime.min.time()) + timedelta(hours=datetime.now().hour,
                                                                                           minutes=datetime.now().minute,
                                                                                           seconds=datetime.now().second)

        cambioValor = request.form['cambioValor']
        #tipoMonedaId = int(request.form['TipoMonedaId'])
        descripcion = request.form['Descripcion']


        bancoDestinoId = session['cajaDolaresId']


        if cambioValor=="Soles":
            logging.info('Ingreso al SUB 3 IF')
            tipooperacionid = 2  # Ingreso de efecto S./ por que se vende dolares e ingresa soles.
            tipoCambioValor = valor_venta
            tipoMonedaId = 1 # Tipo de Moneda que ingresa S/
            textoValor = "VENTA : "
            tipoMonedaEnviar = "SOLES "
            tipoMonedaRecibir = "DOLARES "
        else:
            logging.info('Ingreso al SUB 3 ELSE')
            tipooperacionid = 1  # Retiro de efectivo S./  por que se compra dolares
            tipoCambioValor = valor_compra
            tipoMonedaId= 2 # Tipo de Moneda que ingresa $
            textoValor = "COMPRA : "
            tipoMonedaEnviar = "$ "
            tipoMonedaRecibir = "SOLES "

        esRegistro = True
        saldo = actualizarCajaDolar(tipooperacionid, bancoDestinoId, montoEnviar, tipoCambioValor, tipoMonedaId, esRegistro)
        #obtener operacionid
        cur.execute("select nextval('opreaciones_sq');")
        list_operacionid = cur.fetchall()
        operacionid = list_operacionid[0][0]
        comentario = textoValor + str(tipoCambioValor) + "|cajaDescripcion:" + str(
            session['cajaDescripcion']) + "|cajaSolesId:" + str(session['cajaSolesId']) + "|cajaDolaresId:" + str(
            session['cajaDolaresId']) +"|"+ "comentario:" + descripcion

        cur.execute(
            "INSERT INTO operaciones (operacionid, tipooperacionid, monto, fechaoperacion, comentario, tipomonedaid, bancoid, saldo, tipocambio, comision, usuarioid, numerooperacion) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (operacionid, tipooperacionid, montoEnviar, FechaOperacion, comentario, tipoMonedaId, bancoDestinoId, saldo, tipoCambioValor,0,session['usuarioid'],1))
        conn.commit()
        logging.info('operacionid: ' + str(operacionid))
        logging.info('tipooperacionid: ' + str(tipooperacionid))
        logging.info('montoEnviar: ' + str(montoEnviar))
        logging.info('fechaOperacion: ' + str(FechaOperacion))
        logging.info('textoValor: ' + str(textoValor))
        logging.info('tipoCambioValor: ' + str(tipoCambioValor))
        logging.info('descripcion: ' + str(descripcion))
        logging.info('tipoMonedaId: ' + str(tipoMonedaId))
        logging.info('bancoDestinoId: ' + str(bancoDestinoId))
        logging.info('saldo: ' + str(saldo))
        logging.info('tipoCambioValor: ' + str(tipoCambioValor))
        logging.info('usuarioid: ' + str(session['usuarioid']))

        flash('Transferencia registrada con exito.' + ' Moneda:' + str(cambioValor) + ' Tipo de Cambio:' + str(tipoCambioValor) + ' Monto:' + str(montoEnviar),'success')
        tipoCambio.insertar(valor_venta, valor_compra, modalidadid)
        #imprimirventa(textoValor + str(tipoCambioValor), montoEnviar, montoRecibir, tipoMonedaEnviar, tipoMonedaRecibir, Fecha, operacionid)
        #compraventadolarimpresion (textoValor + str(tipoCambioValor), montoEnviar, montoRecibir, tipoMonedaEnviar, tipoMonedaRecibir, Fecha, operacionid)
        logging.info('---------------------Fin de compraventadolar---------------------')
        return render_template('compraventadolar.html', valor_venta=valor_venta, valor_compra=valor_compra, operacionid=operacionid,
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
        return render_template('compraventadolar.html', valor_venta=valor_venta, valor_compra=valor_compra)

def compraventadolarimpresion (tipoCambioValor, montoEnviar, montoRecibir,tipoMonedaEnviar, tipoMonedaRecibir, Fecha, operacionid):
    return render_template('compraventadolarimpresion.html',
                           tipoCambioValor=tipoCambioValor,
                           montoEnviar=montoEnviar,
                           montoRecibir=montoRecibir,
                           tipoMonedaEnviar=tipoMonedaEnviar,
                           tipoMonedaRecibir=tipoMonedaRecibir,
                           Fecha=Fecha,
                           operacionid=operacionid)

def impresion (monto, comision, tipoOperacion):
    return render_template('imprimirNuevaOperacion.html',
                           monto=monto,
                           comision=comision,
                           tipoOperacion=tipoOperacion)

def validarPrimeraOperacion ():
    logging.info('---------------------Inicio de validarPrimeraOperacion---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fecha = str(obtenerFechaActual())
    select = "SELECT count(operacionid) FROM operaciones where estado is null and usuarioid=%s and fechaoperacion>%s"
    cur.execute(select, (session['usuarioid'],fecha))  # Execute the SQL
    list_operacion = cur.fetchall()
    logging.info('---------------------Fin de validarPrimeraOperacion---------------------')

    if int(list_operacion[0][0]) == 0:
        logging.info('Ingreso al IF')
        flash('¡Recuerda validar su efectivo al iniciar operaciones!', 'error')
