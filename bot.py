import asyncio
from aiogram import Bot, Dispatcher, types, F

from aiogram.filters.command import Command
import os

from aiogram.utils.formatting import Text
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv()
GREET_TEXT="Привет, это бот, который на основе вашего голосового сообщения, текстового сообщения, "\
                         "фотографии или видео выдаст подборку музыки для вашего настроения.\n\n"\
                         "Нажми кнопку ниже и выбери, что конкретно ты хочешь мне отправить!"

TOKEN = os.getenv('TELEGRAM_TOKEN')


bot = Bot(token=TOKEN)
dp = Dispatcher()

BUTTONS=("голосовое сообщение","текстовое сообщение","видео","фотография")
def detect_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0:
        return sentiment
    elif sentiment < 0:
        return sentiment
    else:
        return sentiment

@dp.message(Command("start"))
async def start_buttons(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Голосовое сообщение"),
         types.KeyboardButton(text="Текстовое сообщение")],
        [types.KeyboardButton(text="Видео"),
         types.KeyboardButton(text="Фотографию")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True,input_field_placeholder="Выберите тип"
                                                                                                  " сообщения")
    await message.answer(GREET_TEXT, reply_markup=keyboard)

@dp.message(lambda message: message.text.lower() in BUTTONS)
async def button_reply(message: types.Message):
    await message.answer(f'Пришли мне {message.text.lower()},в формате \n<<{message.text}\nсамо сообщение>>\nчтобы я cмог '
                    f' выдать тебе результат!',reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text)
async def analize(message:types.Message):
    print(detect_sentiment(message.text))



async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())