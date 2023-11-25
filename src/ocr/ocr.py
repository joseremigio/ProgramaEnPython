import cv2
import pytesseract
import re
import logging

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def obtenerNumero(url, nombreBanco):
    # Cargar la imagen con OpenCV
    imagen = cv2.imread(url)
    # Convertir la imagen a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    # Aplicar un preprocesamiento de la imagen si es necesario
    # Por ejemplo, puedes aplicar filtrado, binarización o mejora de contraste
    # Aplicar OCR a la imagen con pytesseract
    texto = pytesseract.image_to_string(imagen_gris)
    # Extraer el número de texto obtenido si es posible
    numero = ''.join(filter(str.isdigit, texto))
    if "IZIPAY" in nombreBanco:
        # Usamos una expresión regular para buscar números con decimales en la cadena
        patron = r'\d+\.\d+'  # Busca números enteros seguidos por un punto y luego números decimales
        # Encuentra todos los números con decimales en la cadena
        numeros_con_decimales = re.findall(patron, texto)
        try:
            numero = numeros_con_decimales[0]
        except Exception as ex:
            numero = 0
            logging.info('Error - obtenerNumero : ' + str(ex))

    if "YAPE" in nombreBanco:
        # Usamos una expresión regular para buscar números con decimales en la cadena
        patron = r'(\d{1,3}(?:,\d{3})*(?:\.\d+))'  # Busca números con comas de millar y decimales
        # Encuentra todos los números con decimales en la cadena
        numeros_con_decimales = re.findall(patron, texto)
        try:
            numero = numeros_con_decimales[0]
        except Exception as ex:
            numero = 0
            logging.info('Error - obtenerNumero : ' + str(ex))

    return numero

def obtenerTexto(url, nombreBanco):
    image = cv2.imread(url)
    text = pytesseract.image_to_string(image)
    #cv2.imshow('Image', image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return text