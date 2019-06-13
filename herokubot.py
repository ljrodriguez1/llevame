import os

from django.core.wsgi import get_wsgi_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

import django
django.setup()
#application = get_wsgi_application()

import logging

import re

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from users.models import Usuario, Auto
DESTINO, ACCEPT, FOOTER, OPCION, SAVEDIRECCION, START, VER_VIAJE = range(7)


def start(update, context):
    try:
        user = Usuario.objects.get(pk=update.effective_user.id)
        if user.lat == 0:
            raise Exception("You Have to send a ubication")
        if user.ida != "None":
            reply_keyboard = [['Direccion'],['Ver Viaje']]
            update.message.reply_text(
                'Elige Opcion', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
            return VER_VIAJE
        else:
            reply_keyboard = [['Direccion','Llevame'],['Manejo']]
            update.message.reply_text(
                'Elige Opcion', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
            return OPCION
    except:
        try: 
            user = Usuario.objects.get(pk=update.effective_user.id)
            update.message.reply_text('Acuerdate que la direccion debes enviarla como archivo adjunto, no en palabras', reply_markup=ReplyKeyboardRemove())
        except:
            user = Usuario(id=update.effective_user.id, name=update.effective_user.first_name, last_name=update.effective_user.last_name, username=update.effective_user.id)
            user.save()
            update.message.reply_text(
                'Hola, {} Somos llevame y organizaremos tus turnos. primero debes señalarnos tu direccion \n la direccion no debe ser escrita, sino que deben adjuntar archivo de ubicacion'.format(user.name), reply_markup=ReplyKeyboardRemove())
        return FOOTER


def direccion(update, context):
    reply_keyboard = [["Atras"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    update.message.reply_text('Esta es tu direccion {}'.format(user.name),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    update.message.bot.send_location(update.message.chat.id, user.lat, user.lng)
    update.message.reply_text('Si quieres cambiarla envianos otra direccion, si no escribe atras',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return SAVEDIRECCION


def save_direccion(update, context):
    reply_keyboard = [["OK"]]
    loc = update.message.location
    user = Usuario.objects.get(pk=update.effective_user.id)
    user.lat = loc["latitude"]
    user.lng = loc["longitude"]
    user.save()
    update.message.reply_text('Tu direccion fue editada, puedes verla en el menu direccion',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return START


def manejo(update, context):
    reply_keyboard = [["Ida"], ["vuelta"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    user.manejo = True
    user.save()
    update.message.reply_text('Que bueno que te comprometas con el medio ambiente, Porfavor indicanos si es ida o vuelta',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    """
    for user1 in Usuario.objects.all():
        logger.info("llevame %s: nombre %s", user1.llevame, user1.name)
        if user1.llevame:
            update.message.bot.send_message(user1.uid, "Hola te encontramos una ida")
    """
    return DESTINO


def llevame(update, context):
    reply_keyboard = [["Ida"], ["vuelta"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    user.manejo = False
    user.save()
    update.message.reply_text('Necesitamos saber si quieres buscas una ida o vuelta',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    """
    for user1 in Usuario.objects.all():
        logger.info("Maneja %s: nombre %s", user1.manejo, user1.name)
        if user1.manejo:
            update.message.bot.send_message(user1.uid, "hola alguien quiere ir en tu auto")
    """
    return DESTINO


def destino(update, context):
    reply_keyboard = [["08:30", "10:00", "11:30"], 
                      ["12:50", "14:00", "15:30"],
                      ["17:00", "18:30", "Otro"]]
    opcion = update.message.text
    user = Usuario.objects.get(pk=update.effective_user.id)
    user.ida = opcion
    user.save()
    update.message.reply_text("¿Elegiste {}, A que hora quieres ir?".format(opcion),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return ACCEPT


def accept(update, context):
    reply_keyboard = [["Aceptar"], ["Cancelar Viaje"]]
    opcion = update.message.text
    user = Usuario.objects.get(pk=update.effective_user.id)
    fecha = update.message.date
    if user.manejo:
        user.quiero_manejar(user.ida, opcion, fecha)
        user.save()
        update.message.reply_text("Tu viaje sera {} a las {} de {}".format(user.auto.dia, user.auto.hora, user.auto.ida),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    else:
        user.quiero_viaje(user.ida, opcion, fecha)
        user.save()
        update.message.reply_text("Estamos buscando un viaje para ti el dia {} a las {} de {}".format(user.buscandoviaje.dia, user.buscandoviaje.hora, user.buscandoviaje.ida),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return START


def ver_viaje(update, context):
    user = Usuario.objects.get(pk=update.effective_user.id)
    if user.manejo:
        reply_keyboard = [["Editar", "Eliminar"], ["Atras"]]
        auto = user.auto
        try:
            personas = user.auto.personas.all()
            update.message.reply_text("hay {} personas en tu auto \nTu viaje sera {} a las {} de {}".format(str(len(personas)),auto.dia, auto.hora, auto.ida),
                reply_markup=ReplyKeyboardMarkup(reply_keyboard))
        except:
            update.message.reply_text("tu auto esta vacio \nTu viaje sera {} a las {} de {}".format(auto.dia, auto.hora, auto.ida),
                reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    else:
        reply_keyboard = [["Editar Viaje", "Eliminar"], ["Atras"]]
        update.message.reply_text("Estamos buscando un viaje para ti",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return START


def eliminar_viaje(update, context):
    reply_keyboard = [["Aceptar"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    if user.manejo:
        user.auto.delete()
    user.manejo = False
    user.ida = "None"
    user.save()
    if update.message.text.lower() == "cancelar":
        update.message.reply_text("Cancelaste el Viaje",
             reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    else: 
        update.message.reply_text("Tu viaje fue eliminado",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return START


def footer(update, context):
    loc = update.message.location
    user = Usuario.objects.get(pk=update.effective_user.id)
    user.lat = loc["latitude"]
    user.lng = loc["longitude"]
    user.save()
    reply_keyboard = [['Direccion','Llevame'],['Manejo']]
    update.message.reply_text(
        'Todo Esta listo, ya puedes buscar o ofrecer un viaje o editar tu ubicacion', reply_markup=ReplyKeyboardMarkup(reply_keyboard))
    return OPCION


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = "767220717:AAG3wsBO3X8SUPrGUmfKRmIuimEvNZ_0ZIo"
    NAME = "grupo1-llevame"

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            OPCION: [MessageHandler(Filters.regex(re.compile(r'manejo', re.IGNORECASE)), manejo),
                    MessageHandler(Filters.regex(re.compile(r'llevame', re.IGNORECASE)), llevame),
                    MessageHandler(Filters.regex(re.compile(r'direccion', re.IGNORECASE)), direccion)],
            
            VER_VIAJE: [MessageHandler(Filters.regex(re.compile(r'ver viaje', re.IGNORECASE)), ver_viaje),
                    MessageHandler(Filters.regex(re.compile(r'direccion', re.IGNORECASE)), direccion)],

            SAVEDIRECCION: [MessageHandler(Filters.location, save_direccion),
                            MessageHandler(Filters.all, start)],

            FOOTER: [MessageHandler(Filters.location, footer),
                    MessageHandler(Filters.all, start)],

            ACCEPT: [MessageHandler(Filters.all, accept)],

            DESTINO: [MessageHandler(Filters.all, destino)],

            START: [MessageHandler(Filters.regex(re.compile(r'eliminar', re.IGNORECASE)), eliminar_viaje),
                    MessageHandler(Filters.regex(re.compile(r'cancelar viaje', re.IGNORECASE)), eliminar_viaje),
                    MessageHandler(Filters.regex(re.compile(r'^editar$', re.IGNORECASE)), manejo),
                    MessageHandler(Filters.regex(re.compile(r'editar viaje', re.IGNORECASE)), llevame),
                    MessageHandler(Filters.all, start)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    # Add handlers
    dp.add_handler(conv_handler)

    dp.add_error_handler(error)
    #updater.start_polling()
    
    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    updater.idle()
    
