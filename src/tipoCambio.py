import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import config
import psycopg2.extras
from datetime import date, datetime, timedelta
import logging
from flask_login import LoginManager, login_user, logout_user, login_required
from utilitario import obtenerFechaActual, obtenerFechaAnterior

#API
def consultaTipoCambio():
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    Select = "SELECT tipocambioid, valorcompra, valorventa, fecha, estado FROM  tipocambio where modalidadid=2 order by tipocambioid desc limit 1"
    cur.execute(Select)
    list_tipo_cambio = cur.fetchall()
    if len(list_tipo_cambio) == 0:
        valor_compra = 0.000
        valor_venta = 0.000
    else:
        valor_compra = list_tipo_cambio[0][1]
        valor_venta = list_tipo_cambio[0][2]

    response = {
                    'message': 'success',
                    'valor_compra': valor_compra,
                    'valor_venta':valor_venta
                }
    return jsonify(response)

def insertar(valor_venta, valor_compra, modalidadid):
    ipAddress = request.remote_addr
    session['ipAddress'] = ipAddress
    fecha = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(
        "INSERT INTO tipocambio (tipocambioid, valorcompra, valorventa, fecha, modalidadid) VALUES (nextval('tipocambio_sq'),%s ,%s, %s, %s)",
        (valor_compra, valor_venta, fecha, modalidadid))
    conn.commit()
    logging.info('valor_compra: ' + str(valor_compra))
    logging.info('valor_venta: ' + str(valor_venta))
    logging.info('fecha: ' + str(fecha))
    logging.info('modalidadid: ' + str(modalidadid))
    return 'tipo cambio registrado'

def consultar(modalidadid):
    Select = "SELECT tipocambioid, valorcompra, valorventa, fecha, estado FROM  tipocambio" + " where modalidadid= " + str(modalidadid)  + " order by tipocambioid desc limit 1"
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_tipo_cambio = cur.fetchall()
    if len(list_tipo_cambio) == 0:
        valor_compra = 0.000
        valor_venta = 0.000
    else:
        valor_compra = list_tipo_cambio[0][1]
        valor_venta = list_tipo_cambio[0][2]
    return valor_compra, valor_venta

def consultarTipoCambioReferencia():
    Select =    " SELECT tipocambioid, valorcompra, valorventa, fecha, estado FROM  tipocambio" \
                " where modalidadid=1" \
                " order by tipocambioid desc" \
                " limit 1 offset 0;"
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_tipo_cambio = cur.fetchall()
    if len(list_tipo_cambio) == 0:
        valor_compra = 3.5
        valor_venta = 3.7
    else:
        valor_compra = list_tipo_cambio[0][1]
        valor_venta = list_tipo_cambio[0][2]
    return valor_compra, valor_venta

def consultarTipoCambioReferenciaPorFecha(fecha):
    Select =    " SELECT tipocambioid, valorcompra, valorventa, fecha, estado FROM  tipocambio" \
                " where " \
                " fecha between '" + fecha + " 00:00:00" "' and  '" + fecha + " 23:59:59" "'" \
                " and modalidadid=1" \
                " order by tipocambioid desc" \
                " limit 1 offset 0;"
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(Select)
    list_tipo_cambio = cur.fetchall()
    if len(list_tipo_cambio) == 0:
        valor_compra = 0.0
        valor_venta = 0.0
    else:
        valor_compra = list_tipo_cambio[0][1]
        valor_venta = list_tipo_cambio[0][2]
    return valor_compra, valor_venta

@login_required
def load():
    if request.method == 'POST':
        valorCompra = request.form['valorCompra']
        valorVenta = request.form['valorVenta']
        modalidadId = request.form['modalidadId']
        insertar(valorVenta, valorCompra, modalidadId)
        flash('Tipo de cambio registrado con exito.', 'success')
        return redirect(url_for('load'))
    else:
        valorCompraPresencial, valorVentaPresencial = consultar(1)
        valorCompraVirtual, valorVentaVirtual = consultar(2)
        return render_template('tipoCambio.html', valorCompraPresencial=valorCompraPresencial, valorVentaPresencial=valorVentaPresencial, valorCompraVirtual=valorCompraVirtual, valorVentaVirtual=valorVentaVirtual)