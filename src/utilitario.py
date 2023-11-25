from datetime import date, datetime, timedelta, time

def obtenerFechaActual():
    fechaDeHoy = datetime.now().strftime("%Y-%m-%d")
    # Obtener la fecha actual
    fecha_actual = datetime.now().date()
    # Calcular la fecha de ayer restando un día
    fecha_de_ayer = fecha_actual + timedelta(days=0)
    fecha_de_ayer.strftime("%Y-%m-%d")
    fechaDeHoy = fecha_de_ayer
    return fechaDeHoy

def obtenerFechaAnterior(Fecha):
    try:
        # Definir un objeto timedelta con un día
        un_dia = timedelta(days=1)
        # Restar un día a la fecha actual
        #Convert str to Date
        Fecha = datetime.strptime(str(Fecha), "%Y-%m-%d")
        FechaAnterior = Fecha - un_dia
    except Exception as e:
        print(e)
    finally:
        return FechaAnterior