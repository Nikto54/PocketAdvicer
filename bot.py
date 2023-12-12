import telebot
from telebot import types

from functions import (
    process_text_message,
    process_audio_message,
    process_photo_message,
)

bot = telebot.TeleBot('6317401550:AAG1C7BEb47jr4IFAzuktRvl6HOdKC7mnl4')


@bot.message_handler(commands=['start'])
def start_message(message):
    global user_id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Текстовое сообщение')
    item2 = types.KeyboardButton('Аудио сообщение')
    item3 = types.KeyboardButton('Фото')
    markup.add(item1, item2, item3)
    user_id=message.from_user.id

    bot.send_message(message.chat.id, 'Привет, я бот который на основе аудиофайла, текстового сообщения '
                                      'или же фото смогу подобрать фильм по твоему настроению', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Текстовое сообщение':
        bot.send_message(message.chat.id, 'Введите текстовое сообщение:', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_text_message, bot)

    elif message.text == 'Аудио сообщение':
        bot.send_message(message.chat.id, 'Пришлите аудиофайл', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_audio_message, bot)

    elif message.text == 'Фото':
        bot.send_message(message.chat.id, 'Пришлите фотографию', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_photo_message, bot)

    else:
        bot.send_message(message.chat.id, 'Нет команды из списка,повторите ввод')


if __name__ == '__main__':
    bot.polling()
