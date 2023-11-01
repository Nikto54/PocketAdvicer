import telebot
from matplotlib import pyplot as plt
from telebot import types
from translate import Translator
from textblob import TextBlob
from fer import FER
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
detector = FER()
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
        bot.register_next_step_handler(message, process_text_message)
    elif message.text == 'Аудио сообщение':
        # Добавьте код для обработки аудио сообщения
        pass
    elif message.text == 'Фото':
        bot.send_message(message.chat.id, 'Пришлите фотографию')
        bot.register_next_step_handler(message, process_photo_message)

def process_text_message(message):
    text = message.text
    translator = Translator(from_lang='ru',to_lang="en")
    translated_text = translator.translate(text)
    print(translated_text,text)

    blob = TextBlob(translated_text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0:
        bot.send_message(message.chat.id,"Положительное настроение")
    elif sentiment < 0:
        bot.send_message(message.chat.id, "Отрицательное настроение")
    else:
        bot.send_message(message.chat.id,"Нейтральное настроение")

def process_photo_message(message):
    translator = Translator(from_lang='en', to_lang="ru")
    photo = message.photo[-1]
    file_id = photo.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    photo_path = r'C:\Users\Богдан ебик\PycharmProjects\PocketAdvicer\photo.jpg'
    with open(photo_path, 'wb') as photo_file:
        photo_file.write(downloaded_file)
    test_image_one = plt.imread(r"C:\Users\Богдан ебик\PycharmProjects\PocketAdvicer\photo.jpg")
    emo_detector = FER(mtcnn=True)
    dominant_emotion, emotion_score = emo_detector.top_emotion(test_image_one)
    bot.send_message(message.chat.id, f'Эмоция {translator.translate(dominant_emotion)}')
    os.remove(r"C:\Users\Богдан ебик\PycharmProjects\PocketAdvicer\photo.jpg")


bot.polling()