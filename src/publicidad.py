from flask import Flask, render_template, request, redirect, url_for, flash, session
import logging
import config
import psycopg2
import psycopg2.extras
from decimal import Decimal
from flask_login import LoginManager, login_user, logout_user, login_required

from datetime import date, datetime, timedelta
import requests


def display_video(filename):
	#print('display_video filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

def showPublicidad ():
    return render_template('publicidad/publicdad.html')

def showTipoCambio ():
    url = 'https://api.kasaseguro.com/api/tipocambio/'
    respuesta = requests.get(url)
    # Verificar el código de estado de la respuesta
    if respuesta.status_code == 200:
        # Extraer el valor deseado de la respuesta JSON
        datos = respuesta.json()
        valor_venta = datos['valor_venta']
        valor_compra = datos['valor_compra']
        return render_template('publicidad/TipoCambio.html',valor_venta=valor_venta, valor_compra=valor_compra)
    else:
        return "Error"