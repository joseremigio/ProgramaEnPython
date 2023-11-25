from flask import session

import psycopg2
from psycopg2.extras import DictCursor
import logging

def get_db_connection():
    bdRemote = False
    #if (session['ipAddress']=='164.90.247.231' or session['ipAddress']=='137.184.88.243'):
    if (False):
        DB_HOST = "localhost"
        DB_NAME = "agente"
        DB_USER = "agenteuser"
        DB_PASS = "postgres"
    else:
        DB_HOST = "localhost"
        DB_NAME = "agente_2023"
        DB_USER = "postgres"
        DB_PASS = "postgres"

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    #conn = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    return conn

def execute_query(query, params=None, fetchone=False, fetchall=False):
    connection = None
    result = None
    logging.info('---------------------Inicio de execute_query---------------------')
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=DictCursor)

        cursor.execute(query, params)

        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            connection.commit()

    except Exception as e:
        logging.error(e)
        if connection:
            connection.rollback()
        raise e

    finally:
        logging.info('---------------------Fin de execute_query---------------------')
        if connection:
            connection.close()

    return result
