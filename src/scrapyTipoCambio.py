from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import asyncio
import logging
from datetime import date, datetime, timedelta
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session

async def obtenerTipoCambioTuCambistaAsync():
    logging.info('Inicio de funcion obtenerTipoCambioTuCambistaAsync')
    url = 'https://tucambista.pe/'
    asession = AsyncHTMLSession()
    r = await asession.get(url)
    await r.html.arender()
    tipoCambioCompra = r.html.xpath('//*[@id="__next"]/div/div[1]/section/div/div/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/button[1]/div[2]/span[1]', first=True).text
    tipoCambioVenta = r.html.xpath('//*[@id="__next"]/div/div[1]/section/div/div/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/button[2]/div[2]/span[1]', first=True).text
    await asession.close()
    logging.info('fin de funcion obtenerTipoCambioTuCambistaAsync')
    return tipoCambioCompra +"|"+ tipoCambioVenta

#sale error en DigitalOcean
def obtenerTipoCambioTuCambista():
    try:
        logging.info('Inicio de funcion obtenerTipoCambioTuCambista')
        url = 'https://tucambista.pe/'
        s = HTMLSession()
        r= s.get(url)
        ##r.html.render(timeout=40)
        r.html.render(sleep=10)
        tipoCambioCompra = r.html.xpath('//*[@id="__next"]/div/div[1]/section/div/div/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/button[1]/div[2]', first=True).text
        tipoCambioVenta  = r.html.xpath('//*[@id="__next"]/div/div[1]/section/div/div/div/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/button[2]/div[2]', first=True).text
        s.close()
        logging.info('Fin de funcion obtenerTipoCambioTuCambista')
        return tipoCambioVenta , tipoCambioCompra
    except Exception as e:
        logging.info('Ocurrió un error: %s', e)

def obtenerTipoCambioKambista():
    try:
        logging.info('Inicio de funcion obtenerTipoCambioKambista')
        url = 'https://kambista.com/'
        s = HTMLSession()
        r= s.get(url)
        tipoCambioVenta = r.html.xpath('// *[ @ id = "valventa"]', first=True).text
        tipoCambioCompra = r.html.xpath('// *[ @ id = "valcompra"]', first=True).text
        s.close()
        logging.info('Fin de funcion obtenerTipoCambioKambista')
        return tipoCambioVenta , tipoCambioCompra
    except Exception as e:
        logging.info('Ocurrió un error: %s', e)

def obtenerYactualizarTipoCambio():
    fecha = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.info(fecha + "-  Inicio de funcion obtenerYactualizarTipoCambio")
    tipoCambioVenta, tipoCambioCompra = obtenerTipoCambioKambista()
    modalidadid=2 #VIRTUAL:2 PRESENCIAL:1
    logging.info(fecha + " - tipoCambioVenta:" + tipoCambioVenta + " tipoCambioCompra:" + tipoCambioCompra)
    if (tipoCambioVenta!="0.000" and tipoCambioCompra!="0.000"):
        #url = "http://192.168.1.40:8000/api/tipocambio/insertar/"+tipoCambioVenta+"/"+tipoCambioCompra+"/"+ str(modalidadid)
        url = "https://agente.kasaseguro.com/api/tipocambio/insertar/" + tipoCambioVenta + "/" + tipoCambioCompra + "/" + str(modalidadid)
        response = requests.get(url)
    logging.info(fecha + " - Fin de funcion obtenerYactualizarTipoCambio")
    return render_template('scrapyTipoCambio.html', tipoCambioVenta=tipoCambioVenta, tipoCambioCompra=tipoCambioCompra, fecha=fecha)


#tipoCambioVenta, tipoCambioCompra = obtenerTipoCambioTuCambista()
#print(obtenerYactualizarTipoCambio())
#logging.info("tipoCambioVenta:" + tipoCambioVenta + " tipoCambioCompra:" + tipoCambioCompra)