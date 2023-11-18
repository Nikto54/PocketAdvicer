import random

import torch
from aniemore.recognizers.text import TextRecognizer
from aniemore.recognizers.voice import VoiceRecognizer
from aniemore.models import HuggingFaceModel
import requests
import soundfile as sf

API_LINK = 'https://api.kinopoisk.dev/v1.4/movie?genres.name={genres_name}&page{count}'


def process_text_message(message, bot):
    text = message.text
    model = HuggingFaceModel.Text.Bert_Tiny2
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tr = TextRecognizer(model=model, device=device)

    emot = tr.recognize(text, return_single_label=True)
    bot.send_message(message.chat.id, f'Ваша основная эмоция сейчас: {emot}')
    message = bot.send_message(message.chat.id, f'Начинается поиск фильма для вас\nПодождите пару секунд')
    found_film(message, bot, emot)


def process_audio_message(message, bot):
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(
        '6317401550:AAG1C'
        '7BEb47jr4IFAzuktRvl6HOdKC7mnl4',
        file_info.file_path
    ))
    with open('voice.ogg', 'wb') as f:
        f.write(file.content)
    data, samplerate = sf.read("data/voice.ogg")
    sf.write("data/voice.wav", data, samplerate)
    model = HuggingFaceModel.Voice.WavLM
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    vr = VoiceRecognizer(model=model, device=device)
    emot = vr.recognize('/content/ваш-звуковой-файл.wav', return_single_label=True)
    bot.send_message(message.chat.id, f'Ваша основная эмоция сейчас: {emot}')
    message = bot.send_message(message.chat.id, f'Начинается поиск фильма для вас\nПодождите пару секунд')
    found_film(message, bot, emot)


# def process_photo_message(message):
#     photo = message.photo[-1]
#     file_id = photo.file_id
#     file_info = bot.get_file(file_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#     photo_path = r'C:\Users\Богдан ебик\PycharmProjects\PocketAdvicer\photo.jpg'
#     with open(photo_path, 'wb') as photo_file:
#         photo_file.write(downloaded_file)
#     test_image_one = plt.imread(r"C:\Users\Богдан ебик\PycharmProjects\PocketAdvicer\photo.jpg")
#     emo_detector = FER(mtcnn=True)
#     dominant_emotion, emotion_score = emo_detector.top_emotion(test_image_one)
#     bot.send_message(message.chat.id, f'Эмоция {translator.translate(dominant_emotion)}')
#     os.remove(r"C:\Users\Богдан ебик\PycharmProjects\PocketAdvicer\photo.jpg")


def found_film(message, bot, emot):
    response = requests.get(
        API_LINK.format(
            genres_name='драма',
            count=random.randint(1, 1000)
        ),
        headers={
            'X-API-KEY': 'B3GFJ69-3MTMFV1-G4JQFRX-9194539',
        }
    ).json()
    response = response['docs'][random.randint(0, 9)]
    bot.edit_message_text(
        f'<b>{response["names"][0]["name"]} ({response["names"][1]["name"]})</b>\n\n'
        f'{response["description"]}',
        chat_id=message.chat.id,
        message_id=message.message_id,
        parse_mode='HTML',
    )
    bot.send_photo(message.chat.id, response["poster"]["url"])