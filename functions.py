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

API_LINK = 'https://api.kinopoisk.dev/v1.4/movie?genres.name={genres_name}&page={count}'

TRANSLATE_DICT_FER = {
    'angry': 'злость',
    'fear': 'страх',
    'happy': 'счастье',
    'neutral': 'нейтральное',
    'sad': 'грусть',
    'surprise': 'удивление'
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

GENRE_DICT = {
    'anger': 'драма',
    'enthusiasm': 'экшн',
    'fear': 'триллер',
    'sadness': 'романтика',
    'happiness': 'комедия',
    'disgust': 'ужасы',
    'angry': 'боевик',
    'happy': 'мюзикл',
    'neutral': 'документальный',
    'sad': 'драма',
    'surprise': 'фантастика'
}


def process_text_message(message, bot):
    try:
        text = message.text
        model = HuggingFaceModel.Text.Bert_Tiny2
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        tr = TextRecognizer(model=model, device=device)
        emot = tr.recognize(text, return_single_label=True)
        bot.send_message(message.chat.id, f'Ваша основная эмоция сейчас: {TRANSLATE_DICT_TEXT.get(emot, emot)}')
        message = bot.send_message(message.chat.id, f'Начинается поиск фильма для вас\nПодождите пару секунд')
        found_film(message, bot, emot)
        ask_for_another_file(message, bot)
    except Exception as e:
        bot.send_message(message.chat.id, e)
        bot.send_message(message.chat.id, 'Вы ввели залупу, Введите текстовое сообщение:')
        bot.register_next_step_handler(message, process_text_message, bot)


def process_audio_message(message, bot):
    try:
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
        bot.send_message(message.chat.id, f'Ваша основная эмоция сейчас: {TRANSLATE_DICT_TEXT.get(emot, emot)}')
        message = bot.send_message(message.chat.id, f'Начинается поиск фильма для вас\nПодождите пару секунд')
        found_film(message, bot, emot)
        os.remove('voice.wav')
        os.remove('voice.ogg')
        ask_for_another_file(message, bot)


    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Вы ввели не тот формат что указали выше!')
        bot.register_next_step_handler(message, process_audio_message, bot)



def process_photo_message(message, bot):
    try:
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
        bot.send_message(message.chat.id, f'Эмоция {TRANSLATE_DICT_FER.get(dominant_emotion, dominant_emotion)}')
        message = bot.send_message(message.chat.id, f'Начинается поиск фильма для вас\nПодождите пару секунд')
        found_film(message, bot, dominant_emotion)
        os.remove("photo.jpg")
        ask_for_another_file(message, bot)


    except Exception as e:
        bot.send_message(message.chat.id, e)
        bot.send_message(message.chat.id, 'Вы ввели не тот формат что указали выше!')
        bot.register_next_step_handler(message, process_photo_message, bot)


def found_film(message, bot, emot):
    response = requests.get(
        API_LINK.format(
            genres_name=GENRE_DICT[emot],
            count=random.randint(1, 1000)
        ),
        headers={
            'X-API-KEY': '8SA53R6-XVQ4FMS-G1QNRAS-CP57ZJD',
        }
    ).json()
    response = response['docs'][random.randint(0, 9)]
    if response['names'][1]:
        bot.edit_message_text(
            f'<b>{response["names"][0]["name"]} ({response["names"][1]["name"]})</b>\n\n'
            f'{response["description"]}',
            chat_id=message.chat.id,
            message_id=message.message_id,
            parse_mode='HTML',
        )
        bot.send_photo(message.chat.id, response["poster"]["url"])
    else:
        bot.edit_message_text(
            f'<b>{response["names"][0]["name"]}</b>\n\n'
            f'{response["description"]}',
            chat_id=message.chat.id,
            message_id=message.message_id,
            parse_mode='HTML',
        )
        bot.send_photo(message.chat.id, response["poster"]["url"])


def ask_for_another_file(message, bot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Текстовое сообщение')
    item2 = types.KeyboardButton('Аудио сообщение')
    item3 = types.KeyboardButton('Фото')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Что бы вы хотели анализировать еще?', reply_markup=markup)

