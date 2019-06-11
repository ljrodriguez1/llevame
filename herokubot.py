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
AGE, GENDER, PHOTO, LOCATION, BIO, FOOTER, OPCION = range(7)


def start(update, context):
    try:
        Usuario.objects.get(pk=update.effective_user.id)
        reply_keyboard = [['Direccion','Llevame'],['Manejo']]
        update.message.reply_text(
            'Elige Opcion', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return OPCION
    except:
        
        user = Usuario(uid=update.effective_user.id, name=update.effective_user.first_name, last_name=update.effective_user.last_name)
        user.save()
        update.message.reply_text(
            'Hola, {} Somos llevame y organizaremos tus turnos. primero debes señalarnos tu direccion'.format(user.name))
        return FOOTER

def direccion(update, context):
    reply_keyboard = [["Hola"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    update.message.reply_text('Ingresa tu Direccion {}'.format(user.name),
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ConversationHandler.END

def manejo(update, context):
    reply_keyboard = [["Ida"], ["vuelta"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    update.message.reply_text('Que bueno que te comprometas con el medio ambiente, Porfavor indicanos si es ida o vuelta',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ConversationHandler.END

def llevame(update, context):
    reply_keyboard = [["Ida"], ["vuelta"]]
    user = Usuario.objects.get(pk=update.effective_user.id)
    update.message.reply_text('Necesitamos saber si quieres buscas una ida o vuelta',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return ConversationHandler.END

def footer(update, context):
    Usuario.objects.get(pk=update.effective_user.id)
    reply_keyboard = [['Direccion','Llevame'],['Manejo']]
    update.message.reply_text(
        'Todo Esta listo, ya puedes buscar o ofrecer un viaje o editar tu ubicacion', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return OPCION

def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Gorgeous! Now, send me your location please, '
                              'or send /skip if you don\'t want to.')

    return LOCATION


def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return BIO


def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


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

            FOOTER: [MessageHandler(Filters.location, footer)],

            GENDER: [MessageHandler(Filters.location, gender)],


            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                        CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text, bio)]
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
    
