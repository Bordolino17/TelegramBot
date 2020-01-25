import requests
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask , request
from dolar import get_dolar
from subte import get_estado
from telegram.ext import Updater , CommandHandler,InlineQueryHandler,Filters,MessageHandler
import telegram.ext
from sqlalchemy import create_engine



ULTIMOVALOR = False
SUSCRIPTORES = list()
tarea = BlockingScheduler(timezone="America/Argentina/Buenos_Aires")

db = create_engine(os.environ["DATABASE_URL"])
res = db.execute("SELECT * from suscriptores")
SUSCRIPTORES = [suscriptor for suc in res for suscriptor in suc]

# if os.path.isfile("suscriptos.txt"):
    # with open("suscriptos.txt","r") as f:
        # suscriptores = f.readlines()
        # for suscriber in suscriptores:
            # SUSCRIPTORES.append(suscriber.replace("\n",""))

if os.path.isfile("dolar.txt"):
    with open("dolar.txt","r") as f:
        ULTIMOVALOR = float(f.readline())

# Handlers manejan las llamadas /saraza

def agregar_suscriptor(id):
    '''
        se agrega un suscriptor a la BD
    '''
    quer = "INSERT INTO suscriptores (suscriptor) values ({})".format(str(id))
    res = db.execute(quer)
    SUSCRIPTORES.append(str(id))
    return
    
def eliminar_suscriptor(id):
    '''
        Se elimina el suscriptor de la BD
    '''
    quer = "DELETE from suscriptores where suscriptor = '{}' ".format(str(id))
    res = db.execute(quer)
    SUSCRIPTORES.remove(str(id))
    return

def suscriptor(id):
    '''
    Verifica si esta suscripto
    '''
   
    return str(id) in SUSCRIPTORES

def start(update,context):
    '''
    Funcion Inicial , Saluda y dice lo que puede hacer 
    '''
    context.bot.send_message(chat_id=update.message.chat_id, text="Buenas "+update.message.chat.first_name+", doy la cotizacion del dolar")

def dolar (update, context):
    '''
        Da la cotizacion de dolar oficial y blue la saco de la api de bluelytics 
    '''
    datos = get_dolar()
    dolar = "{}!!\nDolar Oficial\n"\
                "Compra: ${}\n"\
                "Venta: ${}\n"\
                "Dolar Blue\n"\
                "Compra: ${}\n"\
                "Venta: ${}\n"\
                "Dolar Tarjeta: ${}"\
            .format(update.message.chat.first_name,str(datos["oficial_compra"]),str(datos["oficial_venta"]),\
                str(round(float(datos["blue_compra"]),2)),str(datos["blue_venta"]),str(float(datos["oficial_venta"])*1.30))
    context.bot.send_message(chat_id=update.message.chat_id, text=dolar)
    if not suscriptor(update.message.chat_id):
        suscribir(update, context)
        
def desuscribir(update, context):

    # if update.message.chat_id in SUSCRIPTORES:
        # SUSCRIPTORES.remove(update.message.chat_id)

    '''
        Desuscribe de la lista 
    '''

    if suscriptor(update.message.chat_id):
        eliminar_suscriptor(update.message.chat_id)
        # SUSCRIPTORES.remove(str(update.message.chat_id))

        # with open("suscriptos.txt","w") as file:
            # for suscriber in SUSCRIPTORES:
                # file.write(suscriber+"\n")
        context.bot.send_message(chat_id=update.message.chat_id, text="Se desuscribio con exito")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="No esta suscripto")



def suscribir(update,context):
    '''
        Agrega a la lista para enviar la cotizacion 
    '''
    menu = [["si", "no"]]
    reply_markup = telegram.ReplyKeyboardMarkup(menu)
    updater.bot.send_message(chat_id=update.message.chat_id, 
                 text="Quieres suscribirte?", 
                 reply_markup=reply_markup)
    
def ping(update, context):
    '''
        ¿Vive?
    '''
    context.bot.send_message(chat_id=update.message.chat_id, text="Pong")

def echo(update, context):
    '''
    escucha el texto que le escriben
    '''
    
    reply_markup = telegram.ReplyKeyboardRemove()
    if update.message.text.lower() =="si":
        if suscriptor(update.message.chat_id):
            updater.bot.send_message(chat_id=update.message.chat_id, text="Ya estas suscripto", reply_markup=reply_markup)
            return
        agregar_suscriptor(update.message.chat_id)
        # with open("suscriptos.txt","a") as f:
            # f.write(str(update.message.chat_id)+"\n")
        # SUSCRIPTORES.append(str(update.message.chat_id))
        updater.bot.send_message(chat_id=update.message.chat_id, text="Gracias por suscribirte", reply_markup=reply_markup)
    elif update.message.text.lower() =="no":
        updater.bot.send_message(chat_id=update.message.chat_id, text="Oka, gracias por consultar", reply_markup=reply_markup)
    elif update.message.text.lower() =="💵":
        dolar(update,context)


def programar():
    '''
        Envia la tarea segun el cron 
    '''
    global ULTIMOVALOR
    datos = get_dolar()
    if ULTIMOVALOR == False:
        ULTIMOVALOR = float(datos["oficial_venta"])
    porc = ((float(datos["oficial_venta"])/ULTIMOVALOR)* 100) - 100
    dolar = "Dolar Oficial\n"\
                "Compra: ${} \n"\
                "Venta: ${} | Var: %{}\n"\
                "Dolar Blue\n"\
                "Compra: ${}\n"\
                "Venta: ${}\n"\
                "Dolar Tarjeta: ${}"\
            .format(str(datos["oficial_compra"]),str(datos["oficial_venta"]),round(porc,2),\
            datos["blue_compra"],datos["blue_venta"],(float(datos["oficial_venta"])*1.30))
    with open("dolar.txt","w") as f:
        f.write(datos["oficial_venta"])	
    ULTIMOVALOR = float(datos["oficial_venta"])
    for suscriber in SUSCRIPTORES:
        updater.bot.send_message(chat_id=suscriber, text=dolar)

def subte(update, context):
    '''
        Devuelve el estado del la linea del subte que se le paso
    '''
    linea = " ".join(context.args)
    if linea == '':
        texto = "Debe escribir /subte linea -> donde linea es la linea del subte(a,b,c,d,e,etc) Gracias." 
    else:
        try:
            estados = get_estado()
            texto = estados[linea.upper()]
        except:
            texto ="Linea no valida"
    context.bot.send_message(chat_id=update.message.chat_id, text=texto)

if __name__ == "__main__":
    updater = Updater(token=os.environ["BOT_KEY"],use_context=True)
    dispatcher = updater.dispatcher # dispatchet es el callback (escucha)
    dispatcher.add_handler(CommandHandler('start',start))
    dispatcher.add_handler(CommandHandler('dolar',dolar))
    dispatcher.add_handler(CommandHandler('suscribir',suscribir))
    dispatcher.add_handler(CommandHandler('desuscribir',desuscribir))
    dispatcher.add_handler(CommandHandler('ping',ping))
    dispatcher.add_handler(CommandHandler('subte',subte))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    tarea.add_job(programar, 'cron', month='1-12', day_of_week='mon-fri',hour='10-16')
    port = int(os.environ.get("PORT", 5000))
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=os.environ["BOT_KEY"])
                          
    updater.bot.set_webhook("URLwebhook" + os.environ["BOT_KEY"]) #--> donde va a estar hosteado
    tarea.start()
    updater.idle()
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port, debug = True)
