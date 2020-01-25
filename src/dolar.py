import requests

def get_dolar():
    '''
        Obtengo la cotizacion del dolar oficial y blue
    '''
    valordolar = dict()
    req = requests.get("http://api.bluelytics.com.ar/v2/latest")
    datos = req.json()
    valordolar["oficial_compra"] = str(datos["oficial"]["value_buy"])
    valordolar["oficial_venta"] = str(datos["oficial"]["value_sell"])
    valordolar["blue_compra"] = str(round(datos["blue"]["value_buy"],2))
    valordolar["blue_venta"] = str(datos["blue"]["value_sell"])
    
    return valordolar