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
from datetime import date, datetime, timedelta
from flask import Flask, request, jsonify
from psycopg2 import sql

@login_required
def registraRemesa():
    try:
        if request.method == 'POST':
            fecha               = request.form['fecha']
            monto_salida_sol    = request.form['monto_salida_sol']
            monto_entrada_sol   = request.form['monto_entrada_sol']
            monto_salida_dolar  = request.form['monto_salida_dolar']
            monto_entrada_dolar = request.form['monto_entrada_dolar']

            tipooperacionidSalida = 1 #Salida de Efectivo (RETIRO)
            tipomonedaidSol = 1 # S./
            tipooperacionidEntrada = 2  # Ingreso de Efectivo (DEPOSITO)
            tipomonedaidDolar = 2  # $

            #elimianos en caso existan regitros
            eliminarRemesa(fecha)

            #insertamos nuevos registros
            insert_query = sql.SQL("""
                INSERT INTO remesa (montoenvio, montoretiro, tipomonedaid, fecha)
                VALUES (%s, %s, %s, %s)
            """)

            params = (monto_entrada_sol, monto_salida_sol, tipomonedaidSol, fecha)
            config.execute_query(insert_query, params)

            params = (monto_entrada_dolar, monto_salida_dolar, tipomonedaidDolar, fecha)
            config.execute_query(insert_query, params)

            flash('Se registró remesa con exito con fecha: ' + fecha, 'success')
            return redirect(url_for('listaRemesa'))
        else:
            fecha = str(obtenerFechaActual())
            return render_template('wu/RegistraRemesa.html',fecha=fecha)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@login_required
def listaRemesa():
    if request.method == 'POST':
        fechaInicio = request.form['startDate']
        fechaFin = request.form['endDate']
        TipoMonedaId = request.form['TipoMonedaId']
    else:
        fechaInicio = str(obtenerFechaActual())
        fechaFin = fechaInicio
        TipoMonedaId = 1

    params =(fechaInicio, fechaFin + " 23:59:59", TipoMonedaId)
    list_remesas = consultarRemesa(fechaInicio, fechaFin, TipoMonedaId)

    select_query = "select tipomonedaid , nombre from tipomoneda "
    list_tipomoneda = config.execute_query(select_query, params, False, True)
    return render_template('wu/ListaRemesa.html',
                           list_remesas=list_remesas,
                           fechaInicio=fechaInicio,
                           fechaFin=fechaFin,
                           list_tipomoneda=list_tipomoneda,
                           tipoMonedaSelectedId=TipoMonedaId
    )

def consultarRemesa(fechaInicio,fechaFin,TipoMonedaId):
    select_query = "select ROW_NUMBER () OVER(ORDER BY remesaid DESC) as indice, " \
                   "re.fecha, " \
                   "re.montoretiro, " \
                   "re.montoenvio, " \
                   "re.montoretiro - re.montoenvio as diferencia " \
                   "FROM remesa re " \
                   "left join tipomoneda tm on tm.tipomonedaid =  re.tipomonedaid " \
                   "where re.fecha between %s and  %s and re.tipomonedaid = %s " \
                   "ORDER BY re.fecha; "
    params =(fechaInicio, fechaFin + " 23:59:59", TipoMonedaId)
    list_remesas = config.execute_query(select_query, params, False, True)
    return list_remesas

def calcularRemesaDeHoy ():
    try:
        fechaInicio = str(obtenerFechaActual())
        fechaFin = fechaInicio
        TipoMonedaId = 1
        params = (fechaInicio, fechaFin + " 23:59:59", TipoMonedaId)
        list_remesas = consultarRemesa(fechaInicio, fechaFin, TipoMonedaId)
        saldo_soles_hoy = list_remesas[0][4] #- list_remesas[0][3]

        TipoMonedaId = 2
        params = (fechaInicio, fechaFin + " 23:59:59", TipoMonedaId)
        list_remesas = consultarRemesa(fechaInicio, fechaFin, TipoMonedaId)
        saldo_dolares_hoy = list_remesas[0][4]# - list_remesas[0][3]

    except Exception as e:
        saldo_soles_hoy = 0
        saldo_dolares_hoy = 0
    finally:
        return saldo_soles_hoy ,saldo_dolares_hoy

def eliminarRemesa(fecha):
    try:
        delete_query = sql.SQL("DELETE FROM remesa WHERE fecha = '" + fecha + "'")
        config.execute_query(delete_query)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

