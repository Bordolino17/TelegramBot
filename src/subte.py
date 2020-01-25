from requests import get
from bs4 import BeautifulSoup
import sys

def get_estado():
    '''
    Obtengo el estado de las lineas del subte
    '''
    url = "https://enelsubte.com/estado/"
    datos = dict()
    data = list()
    respuesta = get(url)
    html = BeautifulSoup(respuesta.text, "html.parser")
    tabla = html.find("table", attrs = {"id":"tabla-estado"})
    cuerpo = tabla.find("tbody")
    columnas = cuerpo.find_all("tr")

    for col in columnas:
        cols = col.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
        
    for dato in data:
        if len(dato) >=2:
            datos[dato[0]] = dato[1]
    return datos

 
    

