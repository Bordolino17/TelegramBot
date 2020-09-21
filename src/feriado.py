import requests
from datetime import date
def es_feriado():
    '''
        Devuelve true si es feriado
    '''
    dia , mes ,year  = date.today().day , date.today().month-1 ,date.today().year # se resta 1 al mes por que se toma 0 como mes 1 en la api
    url = f'http://nolaborables.com.ar/api/v2/feriados/{year}?formato=mensual'
    feriados = requests.get(url).json()
    return str(dia) in feriados[mes]

