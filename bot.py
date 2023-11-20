import telebot
from telebot import types
# from fer import FER
# import os

from functions import (
    process_text_message,
    process_audio_message,
    # process_photo_message,
)

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# detector = FER()
bot = telebot.TeleBot('6317401550:AAG1C7BEb47jr4IFAzuktRvl6HOdKC7mnl4')


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Текстовое сообщение')
    item2 = types.KeyboardButton('Аудио сообщение')
    item3 = types.KeyboardButton('Фото')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Привет, я бот который на основе аудиофайла, текстового сообщения '
                                      'или же фото смогу подобрать музыку по твоему настроению', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Текстовое сообщение':
        bot.send_message(message.chat.id, 'Введите текстовое сообщение:')
        bot.register_next_step_handler(message, process_text_message, bot)

    elif message.text == 'Аудио сообщение':
        bot.send_message(message.chat.id, 'Пришлите аудиофайл')
        bot.register_next_step_handler(message, process_audio_message, bot)

    # elif message.text == 'Фото':
    #     bot.send_message(message.chat.id, 'Пришлите фотографию')
    #     bot.register_next_step_handler(message, process_photo_message, bot)


if __name__ == '__main__':
    bot.polling()
