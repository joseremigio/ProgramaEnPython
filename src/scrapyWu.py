from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from bs4 import BeautifulSoup
from lxml import etree
import logging

def boletaWu():
    try:
        logging.info('---------------------Inicio de boletaWu---------------------')
        if request.method == 'POST':

            url = request.form['url']
            MON_REC = request.form['montoRecibido']
            TIPO_MONEDA = request.form['tipoMoneda']
            IMP_TOT = request.form['importeTotal']
            MON_PAG = request.form['montoPagado']
            TASA_CAM = request.form['tipoCambio']

            # Realiza una solicitud GET a la URL
            response = requests.get(url)

            # Verifica si la solicitud fue exitosa (código de estado 200)
            if response.status_code == 200:
                logging.info('status_code = 200')
                # Captura el contenido HTML de la página
                contenido_html = response.text
                logging.info('contenido_html:' + str(contenido_html))
                # Utiliza BeautifulSoup para analizar el contenido HTML
                soup = BeautifulSoup(contenido_html, 'html.parser')
                logging.info('soup:' + str(soup))
                filas_fontcls5 = soup.find_all('tr')

                filas_fontcls5[35].find_all('td')[2].string = MON_REC
                filas_fontcls5[36].find_all('td')[2].string = TIPO_MONEDA
                filas_fontcls5[41].find_all('td')[2].string = IMP_TOT
                filas_fontcls5[43].find_all('td')[2].string = MON_PAG
                filas_fontcls5[44].find_all('td')[2].string = TASA_CAM

                # Obtén el HTML modificado
                contenido_html_modificado = str(soup)

                return render_template('wu/ScrapyPlantilla.html', contenido_html=contenido_html_modificado)
        else:
            return render_template('wu/ScrapyBoletaWu.html')

    except requests.exceptions.RequestException as e:
        logging.error(e)
        return f"Error al capturar la página web: {str(e)}"
    finally:
        logging.info('---------------------Fin de boletaWu---------------------')

def ejemplo():
    return render_template('wu/ScrapyEjemplo.html')
