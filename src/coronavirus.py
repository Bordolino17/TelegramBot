import requests

def get_coronavirus():
    '''
        Datos del Coronavirus en Argentina
    '''
    
    req = requests.get('https://thevirustracker.com/free-api?countryTotal=AR', headers={"User-Agent": "XY"})
    datos = req.json()
    total_casos = datos["countrydata"][0]["total_cases"]
    recuperados = datos["countrydata"][0]["total_recovered"]
    muertos = datos["countrydata"][0]["total_deaths"]
    mensaje = 'Coronavirus en Argentina:\n'\
        'Total de casos: {} \n' \
        'Recuperados : {} \n' \
        'Muertos: {}'.format(total_casos,recuperados,muertos)
    return mensaje


