from flask import Flask, render_template, request, redirect, url_for, flash
import logging
import config
import psycopg2.extras
from datetime import date, datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required

@login_required
def capital():
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    Select = "SELECT capitalid, monto, fecha, utilidad, comentario, tipo from capital  "
    Select = Select + " order by capitalid"
    cur.execute(Select)
    list_capital = cur.fetchall()
    return render_template('capital.html', list_capital=list_capital)

@login_required
def add_capital():
    conn = config.get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    fecha = datetime.now().strftime("%Y-%m-%d")
    if request.method == 'POST':
        if request.form['accion_btn'] == 'registrar':  # registrar
            Select = "SELECT count(capitalid) from capital where fecha= '" + fecha + "'"
            cur.execute(Select)
            list_caja = cur.fetchall()
            if int(list_caja[0][0]) > 0:
                flash('Ya se tiene regsitrado un Capital para la fecha:' + fecha, 'error')
                return redirect(url_for('capital'))
            monto = float(request.form['monto'])
            comentario = request.form['comentario']

            Insert = "INSERT INTO capital (capitalid, monto, comentario, fecha, utilidad) VALUES (nextval('capital_sq'),%s,%s,%s,0)"
            cur.execute(Insert, (monto, comentario, fecha))
            conn.commit()
            flash('Se registró capital con exito con fecha: ' + fecha, 'success')
            return redirect(url_for('capital'))
        if request.form['accion_btn'] == 'actualizar':  # actualizar
            capitalid = int(request.form['capitalid'])
            monto = float(request.form['monto'])
            comentario = request.form['comentario']
            update = "UPDATE capital SET monto=%s, comentario=%s, fecha=%s where capitalid=%s"
            cur.execute(update, (monto, comentario, fecha, capitalid))
            conn.commit()
            flash('Se actualizó capital con exito con fecha: ' + fecha, 'success')
            return redirect(url_for('capital'))