import os
import random
import torch
from aniemore.recognizers.text import TextRecognizer
from aniemore.recognizers.voice import VoiceRecognizer
from aniemore.models import HuggingFaceModel
import requests
import soundfile as sf
from fer import FER
from matplotlib import pyplot as plt
from telebot import types
from database import (add_user, add_country, add_time_interval, get_random_country_for_user,get_random_year_for_user
,find_user)

API_LINK = 'https://api.kinopoisk.dev/v1.4/movie?genres.name={genres_name}&page={count}'

TRANSLATE_DICT_FER = {
    'angry': 'злость',
    'fear': 'страх',
    'happy': 'счастье',
    'neutral': 'нейтральная',
    'sad': 'грусть',
    'surprise': 'удивление',
    None: 'нейтральная'
}
TRANSLATE_DICT_TEXT = {
    'neutral': 'нейтральное',
    'anger': 'злость',
    'enthusiasm': 'воодушевление',
    'fear': 'страх',
    'sadness': 'грусть',
    'happiness': 'счастье',
    'disgust': 'отвращение',

}
print(API_LINK)
GENRE_DICT = {
    'anger': 'драма',
    'enthusiasm': 'фантастика',
    'fear': 'триллер',
    'sadness': 'драма',
    'happiness': 'комедия',
    'disgust': 'ужасы',
    'angry': 'боевик',
    'happy': 'мюзикл',
    'neutral': 'документальный',
    'sad': 'драма',
    'surprise': 'фантастика'
}


def ask_for_another_file(message, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Текстовое сообщение')
    item2 = types.KeyboardButton('Аудио сообщение')
    item3 = types.KeyboardButton('Фото')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Что бы вы хотели анализировать еще?', reply_markup=markup)


def process_text_message(message, bot):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Мои предпочтения')
        item2 = types.KeyboardButton('Случайный фильм')
        markup.add(item1, item2)
        text = message.text
        model = HuggingFaceModel.Text.Bert_Tiny2
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        tr = TextRecognizer(model=model, device=device)
        emot = tr.recognize(text, return_single_label=True)
        bot.send_message(message.chat.id, f'Ваша основная эмоция сейчас: {TRANSLATE_DICT_TEXT.get(emot, emot)}',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, f'Хотите выбрать случайный фильм или по вашим предпочтениям?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, extends_found_film, bot, emot)



    except Exception as e:
        bot.send_message(message.chat.id, 'Вы ввели не тот формат,что указали выше, Введите текстовое сообщение:')
        print(e)
        bot.register_next_step_handler(message, process_text_message, bot)


def process_audio_message(message, bot):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Мои предпочтения')
        item2 = types.KeyboardButton('Случайный фильм')
        markup.add(item1, item2)
        file_info = bot.get_file(message.voice.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(
            '6317401550:AAG1C'
            '7BEb47jr4IFAzuktRvl6HOdKC7mnl4',
            file_info.file_path
        ))
        with open('voice.ogg', 'wb') as f:
            f.write(file.content)
        data, samplerate = sf.read("voice.ogg")
        sf.write("voice.wav", data, samplerate)
        model = HuggingFaceModel.Voice.WavLM
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        vr = VoiceRecognizer(model=model, device=device)
        emot = vr.recognize('voice.wav', return_single_label=True)
        os.remove('voice.wav')
        os.remove('voice.ogg')
        bot.send_message(message.chat.id, f'Ваша основная эмоция сейчас: {TRANSLATE_DICT_TEXT.get(emot, emot)}',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, f'Хотите выбрать случайный фильм или по вашим предпочтениям?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, extends_found_film, bot, emot)

    except Exception as e:
        bot.send_message(message.chat.id, 'Вы ввели не тот формат что указали выше!')
        bot.register_next_step_handler(message, process_audio_message, bot)


def process_photo_message(message, bot):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('Мои предпочтения')
        item2 = types.KeyboardButton('Случайный фильм')
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        photo_path = 'photo.jpg'
        detector = FER(mtcnn=True)
        with open(photo_path, 'wb') as photo_file:
            photo_file.write(downloaded_file)
        test_image_one = plt.imread("photo.jpg")
        dominant_emotion, emotion_score = detector.top_emotion(test_image_one)
        bot.send_message(message.chat.id,
                         f'Ваша основная эмоция сейчас: {TRANSLATE_DICT_FER.get(dominant_emotion, dominant_emotion)}',
                         markup=types.ReplyKeyboardRemove())
        os.remove("photo.jpg")
        bot.send_message(message.chat.id, f'Хотите выбрать случайный фильм или по вашим предпочтениям?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, extends_found_film, bot,
                                       TRANSLATE_DICT_FER.get(dominant_emotion, dominant_emotion))


    except Exception as e:
        bot.send_message(message.chat.id, 'Вы ввели не тот формат что указали выше!')
        bot.register_next_step_handler(message, process_photo_message, bot)


def found_film(message, bot, emot, link=API_LINK):
    message = bot.send_message(message.chat.id, f'Начинается поиск фильма для вас\nПодождите пару секунд')
    global response
    if ('countries' and 'year') in link:
        response = requests.get(
            API_LINK.format(
                genres_name=GENRE_DICT[emot],
                count=random.randint(1, 1000),
                countriess=get_random_country_for_user(message.from_user.id),
                years=get_random_year_for_user(message.from_user.id)
            ),
            headers={
                'X-API-KEY': '132Z32C-5Y044XJ-H0DXA4A-M5JCFYH',
            }
        ).json()
        print(link)
        if len(response['docs']) == 0:
            found_film(message, bot, emot)
        response = response['docs'][random.randint(0, len(response['docs']) - 1)]
        if response.get('description') is not None and response.get('poster') != None and len(response['names']) > 1:
            bot.send_message(message.chat.id,
                f'<b>{response["names"][0]["name"]} ({response["names"][1]["name"]})</b>\n\n'
                f'{response["description"]}',
                parse_mode='HTML',
            )
            bot.send_photo(message.chat.id, response["poster"]["url"])


    else:
        response = requests.get(
            API_LINK.format(
                genres_name=GENRE_DICT[emot],
                count=random.randint(1, 1000)
            ),
            headers={
                'X-API-KEY': '132Z32C-5Y044XJ-H0DXA4A-M5JCFYH',
            }
        ).json()
        if len(response['docs']) == 0:
            found_film(message, bot, emot)
        response = response['docs'][random.randint(0, len(response['docs']) - 1)]
        if response.get('description') is not None and response.get('poster') != None and len(response['names']) > 1:
            bot.send_message(message.chat.id,
                f'<b>{response["names"][0]["name"]} ({response["names"][1]["name"]})</b>\n\n'
                f'{response["description"]}',
                             parse_mode='HTML',
            )
            bot.send_photo(message.chat.id, response["poster"]["url"])


        else:
            found_film(message, bot, emot)


def extends_found_film(message, bot, emot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Другой фильм')
    item2 = types.KeyboardButton('Мне нравится фильм')
    markup.add(item1, item2)
    text = message.text

    if (text == "Случайный фильм" or text == "Другой фильм") :
        found_film(message, bot, emot)
        bot.send_message(message.chat.id, f'Выберите одну из опций ниже',
                                   reply_markup=markup)
        bot.register_next_step_handler(message, extends_found_film,*[bot, emot])
    if text == 'Мне нравится фильм':
        print(message.from_user.id)
        add_user(message.from_user.id)
        year = response['year']

        country_names = [country['name'] for country in response['countries']]
        for i in country_names:
            add_country(message.from_user.id, i)
        add_time_interval(message.from_user.id, year - year % 10, year + 9 - year % 10)
        bot.send_message(message.chat.id, f'Фильм добавлен в ваши предпочтения,в следующий раз будут '
                                                    f'искаться похожие фильмы',
                                   reply_markup=types.ReplyKeyboardRemove())
        #bot.register_next_step_handler(message, ask_for_another_file(message,bot))

    if text == 'Мои предпочтения':

        if find_user(message.from_user.id):
            get_random_country_for_user(message.from_user.id)
            found_film(message, bot, emot,link=API_LINK+'&year={yearss}&countries.name={countriess}')
            message = bot.send_message(message.chat.id, f'Выберите одну из опций ниже',
                                       reply_markup=markup)
            bot.register_next_step_handler(message, extends_found_film, bot, emot)
        else:
            bot.send_message(message.chat.id, f'Вас еще нет в нашей базе,поэтому сначала нужно оценить любой фильм '
                                              f'из тех что будут дальше')
            message.text='Случайный фильм'
            bot.register_next_step_handler(message, extends_found_film(message,bot,emot))





