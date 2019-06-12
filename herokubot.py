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

from users.models import Usuario
DESTINO, ACCEPT, FOOTER, OPCION, SAVEDIRECCION = range(5)


def start(update, context):
    try:
        Usuario.objects.get(pk=update.effective_user.id)
        reply_keyboard = [['Direccion','Llevame'],['Manejo']]
        update.message.reply_text(
            'Elige Opcion', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return OPCION
    except:
        
        user = Usuario(uid=update.effective_user.id, name=update.effective_user.first_name, last_name=update.effective_user.last_name, username=update.effective_user.id)
        user.save()
        update.message.reply_text(
            'Hola, {} Somos llevame y organizaremos tus turnos. primero debes señalarnos tu direccion'.format(user.name))
        return FOOTER

def direccion(update, context):
    reply_keyboard = [["Hola"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    update.message.reply_text('Ingresa tu Direccion {}'.format(user.name),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return SAVEDIRECCION

def save_direccion(update, context):
    reply_keyboard = [["Si"], ["No"]]
    loc = update.message.location
    update.message.reply_text('¿es esta tu direccion?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    update.message.bot.send_location(update.message.chat.id, loc['latitude'], loc['longitude'])
    return ConversationHandler.END

def manejo(update, context):
    reply_keyboard = [["Ida"], ["vuelta"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    user.manejo = True
    user.llevame = False
    user.save()
    update.message.reply_text('Que bueno que te comprometas con el medio ambiente, Porfavor indicanos si es ida o vuelta',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
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
    user.llevame = True
    user.save()
    update.message.reply_text('Necesitamos saber si quieres buscas una ida o vuelta',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    for user1 in Usuario.objects.all():
        logger.info("Maneja %s: nombre %s", user1.manejo, user1.name)
        if user1.manejo:
            update.message.bot.send_message(user1.uid, "hola alguien quiere ir en tu auto")
    return DESTINO

def destino(update, context):
    reply_keyboard = [["08:30", "10:00", "11:30"], 
                      ["12:50", "14:00", "15:30"],
                      ["17:00", "18:30", "Otro"]]
    opcion = update.message.text
    user = Usuario.objects.get(pk=update.effective_user.id)
    update.message.reply_text("¿Elegiste {}, A que hora quieres ir?".format(opcion),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ACCEPT
    
def accept(update, context):
    opcion = update.message.text
    update.message.reply_text("¿Tu viaje sera a las {},".format(opcion),
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def footer(update, context):
    Usuario.objects.get(pk=update.effective_user.id)
    reply_keyboard = [['Direccion','Llevame'],['Manejo']]
    update.message.reply_text(
        'Todo Esta listo, ya puedes buscar o ofrecer un viaje o editar tu ubicacion', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
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

            SAVEDIRECCION: [MessageHandler(Filters.location, save_direccion)],

            FOOTER: [MessageHandler(Filters.location, footer)],

            ACCEPT: [MessageHandler(Filters.all, accept)],

            DESTINO: [MessageHandler(Filters.all, destino)],

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
    
