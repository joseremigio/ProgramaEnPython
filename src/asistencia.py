from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import config
import psycopg2
import psycopg2.extras
from utilitario import obtenerFechaActual
from datetime import date, datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required

def registrar():
    try:
        logging.info('---------------------Inicio de registrar---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        Fecha = obtenerFechaActual()
        #existeAsistencia = consultar()
        cur.execute("select nextval('asistencia_sq');")
        list_AsistenciaId = cur.fetchall()
        AsistenciaId = list_AsistenciaId[0][0]
        session['asistenciaid'] = AsistenciaId

        UsuarioId = session['usuarioid']
        Fecha = obtenerFechaActual()
        HoraInicio = datetime.now().time()

        Insert = "INSERT INTO asistencia (" \
                 "asistenciaid, " \
                 "usuarioid, " \
                 "fecha, " \
                 "horaingreso ) " \
                 "VALUES (%s,%s,%s,%s)"
        cur.execute(Insert, (
            AsistenciaId,
            UsuarioId,
            Fecha,
            HoraInicio
        ))
        conn.commit()
    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('---------------------Fin de registrar------------------------')

def actualizar():
    try:
        logging.info('---------------------Inicio de actualizar---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        AsistenciaId = session['asistenciaid']
        HoraSalida = datetime.now().time()
        Update = "UPDATE asistencia SET horasalida=%s where asistenciaid=%s"
        cur.execute(Update, (HoraSalida, AsistenciaId))
        conn.commit()
    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('---------------------Fin de actualizar------------------------')

def consultar():
    try:
        logging.info('---------------------Inicio de actualizar---------------------')
        conn = config.get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        UsuarioId = session['usuarioid']
        Fecha = obtenerFechaActual()
        Select = "SELECT count(asistenciaid) from asistencia where usuarioid='" + str(UsuarioId) + "'" + " and fecha= '" + Fecha + "'"
        cur.execute(Select)
        lista = cur.fetchall()
        if len(lista)==0:
            existeAsistencia= False
        else:
            existeAsistencia = True

    except Exception as e:
        print(e)
        logging.error(e)
    finally:
        logging.info('---------------------Fin de actualizar------------------------')
        return existeAsistencia

