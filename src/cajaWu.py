from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import config
import psycopg2
import psycopg2.extras
import remesa
from decimal import Decimal
from flask_login import LoginManager, login_user, logout_user, login_required
from tipoCambio import consultarTipoCambioReferencia, consultarTipoCambioReferenciaPorFecha
from datetime import date, datetime, timedelta
from utilitario import obtenerFechaActual, obtenerFechaAnterior

def selectCajaApertura (fechaSeleccionada):
    logging.info('---------------------Inicio de selectCajaApertura---------------------')
    fechaDeHoy = str(obtenerFechaActual())
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    scriptBanco = "SELECT ba.bancoid, " \
                  "ba.nombre, " \
                  "COALESCE((ca.montofinalreal), 0) AS montofinalreal, " \
                  "ca.fecha " \
                  "FROM banco ba "
    scriptBanco = scriptBanco + "left join caja ca on ca.bancoid =ba.bancoid  where ba.eswu =1 "
    scriptBanco = scriptBanco + "order by ca.fecha desc, ba.orden "
    scriptBanco = scriptBanco + "limit (select count(ba.bancoid) from banco ba where ba.eswu =1) "
    cur.execute(scriptBanco)  # Execute the SQL
    list_banco = cur.fetchall()

    nueva_list_banco = []
    for item in list_banco:
        BancoId = int(item[0])
        if BancoId < 30:
            nuevo_item = [item[0], item[1], item[2], item[3]]
        else:
            if BancoId==30 or BancoId==31:
                nuevo_item = [item[0], item[1], 0.0, item[3]]
            else:
                BancoId = BancoId - 2
                FechaAnterior = obtenerFechaAnterior(fechaDeHoy)
                MontoInicial = obtenerMontoInicialWesterUnionDiaAnterior(BancoId, FechaAnterior)
                nuevo_item=[item[0],item[1],MontoInicial,item[3]]
        nueva_list_banco.append(nuevo_item)

    list_banco = nueva_list_banco

    Select = "SELECT c.cajaid, " \
             "c.montoinicial, " \
             "c.montofinalcalculado, " \
             "c.montofinalreal, " \
             "b.nombre " \
             "from caja c " \
             "left join banco b on b.bancoid =c.bancoid "
    Select = Select + "where b.eswu =  1 and c.fecha= '" + str(fechaSeleccionada) + "'"
    Select = Select + " order by c.cajaid"
    cur.execute(Select)
    list_cajas = cur.fetchall()
    logging.info('---------------------Fin de selectCajaApertura---------------------')
    return render_template('wu/AperturaCaja.html', list_banco=list_banco, fecha=fechaSeleccionada, list_cajas=list_cajas, fechaDeHoy=fechaDeHoy)

def consultarMontoInicialDeBancos(fechaSeleccionada):
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    select = "select bancoid, montoinicial from caja where " \
             "fecha between '" + fechaSeleccionada + "' and '" + fechaSeleccionada + " 23:59:59' " \
             "order by bancoid"
    cur.execute(select)
    list = cur.fetchall()
    return list

def consultarSumaDeMontosPorDia(fechaSeleccionada, bancoid):
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    select = "select  sum(montosolbanco), sum(montosolcaja), sum(comisionsol), sum(montodolarbanco), " \
             "sum(montodolarcaja), sum(saldo) " \
             "from operacioneswu op " \
             "where op.fechaoperacion between '" + fechaSeleccionada + "' and '" + fechaSeleccionada + " 23:59:59'"

    if (bancoid!=0):
        select = select + " and op.bancoid=" + str(bancoid)

    cur.execute(select)
    list = cur.fetchall()
    return list

def selectCajaCierre (fechaSeleccionada):
    logging.info('---------------------Inicio de selectCajaCierre---------------------')
    fechaDeHoy = str(obtenerFechaActual())
    fechaSeleccionada = str(fechaSeleccionada)
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    listMontoInicialDeBanco = consultarMontoInicialDeBancos(fechaSeleccionada)
    listSumaMontoPorDia = consultarSumaDeMontosPorDia(fechaSeleccionada, 0)

    sumaMontosolwu      = listSumaMontoPorDia[0][0]
    sumaMontosolwu      = 0 if sumaMontosolwu is None else sumaMontosolwu
    sumaMontosolcaja    = listSumaMontoPorDia[0][1]
    sumaMontosolcaja    = 0 if sumaMontosolcaja is None else sumaMontosolcaja
    sumaComisionsol     = listSumaMontoPorDia[0][2]
    sumaComisionsol     = 0 if sumaComisionsol is None else sumaComisionsol
    sumaMontodolarwu    = listSumaMontoPorDia[0][3]
    sumaMontodolarwu    = 0 if sumaMontodolarwu is None else sumaMontodolarwu
    sumaMontodolarcaja  = listSumaMontoPorDia[0][4]
    sumaMontodolarcaja  = 0 if sumaMontodolarcaja is None else sumaMontodolarcaja
    sumaSaldo           = listSumaMontoPorDia[0][5]
    sumaSaldo           = 0 if sumaSaldo is None else sumaSaldo


    for item in listMontoInicialDeBanco:
        # Total del dia 22=EFECTIVO WU (Caja Principal) - SOLES
        if item[0] == 22:
            #listSumaMontoPorDiaBanco = consultarSumaDeMontosPorDia(fechaSeleccionada, 15)
            #sumaMontosolcaja = listSumaMontoPorDiaBanco[0][1]
            #sumaMontosolcaja = 0 if sumaMontosolcaja is None else sumaMontosolcaja

            montosolcaja = item[1] + sumaMontosolcaja
            montototalcalculado = montosolcaja + sumaComisionsol
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            upDate = "UPDATE caja SET montofinalcalculado=" + str(round(montosolcaja,2)) + ", " \
                     " comisionbanco=" + str(round(sumaComisionsol,2)) + ", " \
                     " montototalcalculado=" + str(round(montototalcalculado,2)) + " " \
                     " where fecha= '" + fechaSeleccionada + " 00:00:00'" \
                     " and bancoid = "+ str(item[0])
            cur.execute(upDate)
            conn.commit()
        # Total del dia 15=WESTER UNION - REMESA - SOLES
        if item[0] == 15:
            listSumaMontoPorDiaBanco = consultarSumaDeMontosPorDia(fechaSeleccionada, item[0])
            sumaMontosolwu = listSumaMontoPorDiaBanco[0][0]
            sumaMontosolwu = 0 if sumaMontosolwu is None else sumaMontosolwu
            montosolwu= item[1] + sumaMontosolwu
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            upDate = "UPDATE caja SET montofinalcalculado=" + str(round(montosolwu,2)) + ", " \
                     " montototalcalculado=" + str(round(montosolwu,2)) + " " \
                     " where fecha= '" + fechaSeleccionada + " 00:00:00'" \
                     " and bancoid = "+ str(item[0])
            cur.execute(upDate)
            conn.commit()

        # Total del dia 23=EFECTIVO WU (Caja Principal) - DOLARES
        if item[0] == 23:
            #listSumaMontoPorDiaBanco = consultarSumaDeMontosPorDia(fechaSeleccionada, 17)
            #sumaMontodolarcaja = listSumaMontoPorDiaBanco[0][4]
            #sumaMontodolarcaja = 0 if sumaMontodolarcaja is None else sumaMontodolarcaja

            montodolarcaja = item[1] + sumaMontodolarcaja
            upDate = "UPDATE caja SET montofinalcalculado=" + str(round(montodolarcaja,2))  + ", " \
                     " montototalcalculado=" + str(round(montodolarcaja,2)) + " " \
                     " where fecha= '" + fechaSeleccionada + " 00:00:00'" \
                     " and bancoid = "+ str(item[0])
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(upDate)
            conn.commit()

        # Total del dmontodolarwu 17=WESTER UNION - REMESA - DOLARES
        if item[0] == 17:
            montodolarwu = item[1] + sumaMontodolarwu
            upDate = "UPDATE caja SET montofinalcalculado=" + str(round(montodolarwu,2)) + ", " \
                     " montototalcalculado=" + str(round(montodolarwu,2)) + " " \
                     " where fecha= '" + fechaSeleccionada + " 00:00:00'" \
                     " and bancoid = "+ str(item[0])
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(upDate)
            conn.commit()

        # Total del 26=BCP - SOLES || 28=SCOTIABANK - SOLES
        if item[0] == 26 or item[0] == 28:
            listSumaMontoPorDiaBanco = consultarSumaDeMontosPorDia(fechaSeleccionada, item[0])
            sumaMontosolwu = listSumaMontoPorDiaBanco[0][0]
            sumaMontosolwu = 0 if sumaMontosolwu is None else sumaMontosolwu

            montosolcaja = item[1] + sumaMontosolwu
            upDate = "UPDATE caja SET montofinalcalculado=" + str(round(montosolcaja, 2)) + ", " \
                     " montototalcalculado=" + str(round(montosolcaja, 2)) + " " \
                     " where fecha= '" + fechaSeleccionada + " 00:00:00'" \
            " and bancoid = "+ str(item[0])
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(upDate)
            conn.commit()

        # Total del 27=BCP - DOLARES || 29=SCOTIABANK - DOLARES
        if item[0] == 27 or item[0] == 29:
            listSumaMontoPorDiaBanco = consultarSumaDeMontosPorDia(fechaSeleccionada, item[0])
            sumaMontodolarwu = listSumaMontoPorDiaBanco[0][3]
            sumaMontodolarwu = 0 if sumaMontodolarwu is None else sumaMontodolarwu

            montodolarcaja = item[1] + sumaMontodolarwu
            upDate = "UPDATE caja SET montofinalcalculado=" + str(round(montodolarcaja, 2)) + ", " \
                     " montototalcalculado=" + str(round(montodolarcaja, 2)) + " "\
                     " where fecha= '" + fechaSeleccionada + " 00:00:00'" \
            " and bancoid = " + str(item[0])
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(upDate)
            conn.commit()


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
             " (select count(operacionid) from operacioneswu op where op.fechaoperacion between '" + fechaSeleccionada + " 00:00:00' and '" + fechaSeleccionada + " 23:59:59' and op.bancoid=c.bancoid and op.comentario not like '%RECARGA%')" \
             "from caja c " \
             "left join banco b on b.bancoid =c.bancoid " \
             "left join operacioneswu o on o.bancoid =c.bancoid  "
    Select = Select + "where c.fecha= '" + fechaSeleccionada + "' and b.eswu=1"
    Select = Select + " group by c.cajaid, c.montoinicial, c.montofinalcalculado, c.montofinalreal, b.nombre, " \
                      " c.comisionbanco, c.montototalcalculado, c.montodolarsol, c.bancoid, c.montodolarsolcalculado, " \
                      " c.montodolarsolreal, b.orden" \
                      " order by b.orden"
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_cajas = cur.fetchall()

    valorCompraVirtualFechaActual, valorVentaVirtualFechaActual = consultarTipoCambioReferenciaPorFecha(fechaSeleccionada)

    fechaSeleccionadaFechaAnterior = str(obtenerFechaAnterior(fechaSeleccionada))
    fechaSeleccionadaFechaAnterior = fechaSeleccionadaFechaAnterior.replace("00:00:00","")
    valorCompraVirtualDiaAnterior, valorVentaVirtualDiaAnterior = consultarTipoCambioReferenciaPorFecha(fechaSeleccionadaFechaAnterior)

    if valorCompraVirtualDiaAnterior==0.0:
        valorCompraVirtualDiaAnterior=valorCompraVirtualFechaActual
        valorVentaVirtualDiaAnterior=valorVentaVirtualFechaActual

    #Obtener remesa del dia
    saldo_soles_hoy ,saldo_dolares_hoy = remesa.calcularRemesaDeHoy()

    logging.info('---------------------Fin de selectCajaCierre---------------------')
    return render_template('wu/CierreCaja.html',
                           list_cajas=list_cajas,
                           fecha=fechaSeleccionada,
                           fechaDeHoy=fechaDeHoy,
                           valorCompraVirtualFechaActual=valorCompraVirtualFechaActual,
                           valorVentaVirtualFechaActual=valorVentaVirtualFechaActual,
                           valorCompraVirtualDiaAnterior=valorCompraVirtualDiaAnterior,
                           valorVentaVirtualDiaAnterior=valorVentaVirtualDiaAnterior,
                           saldo_soles_hoy=saldo_soles_hoy,
                           saldo_dolares_hoy=saldo_dolares_hoy
                           )


@login_required
def cierre():
    try:
        logging.info('---------------------Inicio de cierre---------------------')
        if request.method == 'POST':
            logging.info('Ingreso al IF')
            if request.form['accion_btn'] == 'actualizar':  # actualizar
                logging.info('Ingreso al SUB IF')
                conn = config.get_db_connection()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                for item in request.form:
                    logging.info('Ingreso al FOR')
                    if item.isnumeric():
                        logging.info('Ingreso al SUB SUB IF')
                        MontoFinalReal = request.form[item]
                        CajaId = int(item)
                        Update = "UPDATE caja SET montofinalreal=%s where cajaid=%s"
                        cur.execute(Update, (MontoFinalReal, CajaId))
                        conn.commit()
                        logging.info('CajaId: ' + str(CajaId))
                        logging.info('MontoFinalReal: ' + str(MontoFinalReal))
                flash('Cierre de caja con exito.', 'success')
                # pywhatkit.sendwhatmsg('+51969368883', 'Message 2', datetime.now().hour, datetime.now().minute + 1)
                return redirect(url_for('cierre'))

            else:  # buscar
                logging.info('Ingreso al ELSE')
                return selectCajaCierre(request.form['fechaCierre'])
        else:
            fecha = obtenerFechaActual()
            return selectCajaCierre(fecha)
    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('Fin de cierre')

@login_required
def apertura():
    logging.info('---------------------Inicio de apertura---------------------')
    try:
        if request.method == 'POST':
            conn = config.get_db_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if request.form['accion_btn'] == 'registrar':  # registrar
                Fecha = request.form['fecha']
                Select = "SELECT count(cajaid) from caja where bancoid=22 and fecha= '" + Fecha + "'"
                cur.execute(Select)
                list_caja = cur.fetchall()
                if int(list_caja[0][0]) > 0:
                    flash('Ya se tiene aperturada caja para la fecha:' + Fecha, 'error')
                    return redirect(url_for('cajaApertura'))

                for item in request.form:
                    if item.isnumeric() and int(item) < 100:
                        BancoId = int(item)

                        MontoInicial = request.form[item]
                        # 30:WESTER UNION - REMESA - SOLES (HOY)
                        #if BancoId <30:
                        #    MontoInicial = request.form[item]
                        #else: #Si el bancoId es mayo e igual que 30 se obtiene el monto de dias anteriores.
                        #    MontoInicial = obtenerMontoInicial(BancoId, Fecha)
                        logging.info('MontoInicial: ' + str(MontoInicial))
                        #logging.info('MontoDolarSol: ' + str(MontoDolarSol))
                        logging.info('BancoId: ' + str(BancoId))

                        Insert = "INSERT INTO caja (" \
                                 "cajaid, " \
                                 "bancoid, " \
                                 "montoinicial, " \
                                 "fecha) " \
                                 "VALUES (nextval('caja_sq'),%s,%s,%s)"
                        cur.execute(Insert, (
                                  BancoId,
                                  MontoInicial,
                                  Fecha
                        ))
                        conn.commit()

                flash('Apertura de caja  conexito con fecha: ' + Fecha, 'success')
                return redirect(url_for('apertura'))
            if request.form['accion_btn'] == 'buscar':  # registrar
                return selectCajaApertura(request.form['fecha'])
            else:  # eliminar
                Fecha = request.form['fecha']
                Delete = "DELETE FROM caja WHERE fecha = '" + Fecha + "' and bancoid in (select bancoid from banco where eswu=1)"
                cur.execute(Delete)
                conn.commit()
                Delete = "DELETE FROM operacioneswu WHERE fechaoperacion between %s and  %s "
                cur.execute(Delete, (Fecha, Fecha + " 23:59:59"))
                conn.commit()
                flash('Se elimino con exito la caja wu y operaciones wu de la fecha: ' + Fecha, 'success')
                return selectCajaApertura(Fecha)
        else:
            fecha = str(obtenerFechaActual())
            return selectCajaApertura(fecha)
    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('Fin de apertura')

def obtenerMontoInicial(BancoId, Fecha):
    logging.info('---------------------Inicio de obtenerMontoInicial---------------------')

    try:
        FechaAnterior = obtenerFechaAnterior(Fecha)
        if BancoId==30 or BancoId==31:
            MontoInicial = 0
        else:
            MontoInicial = obtenerMontoInicialWesterUnionDiaAnterior(BancoId, FechaAnterior)

    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('Fin de obtenerMontoInicial')
        return MontoInicial

def obtenerMontoInicialWesterUnionDiaAnterior(BancoId, Fecha):
    logging.info('---------------------Inicio de obtenerMontoInicialWesterUnionDiaAnterior---------------------')
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        Select = "SELECT montofinalreal from caja where bancoid=" + str(BancoId) + " and fecha= '" + str(Fecha) + "'"
        cur.execute(Select)
        lista = cur.fetchall()
        if len(lista)==0:
            MontoInicial = 0
        else:
            MontoInicial = lista[0][0]

    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('Fin de obtenerMontoInicialWesterUnionDiaAnterior')
        return MontoInicial


