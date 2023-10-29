import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_buttons(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Голосовое сообщение"),
         types.KeyboardButton(text="Текстовое сообщение")],
        [types.KeyboardButton(text="Видео"),
         types.KeyboardButton(text="Фотографию")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, row_width=2,resize_keyboard=True)
    await message.answer("Привет, это бот, который на основе вашего голосового сообщения, текстового сообщения, "\
                         "фотографии или видео выдаст подборку музыки для вашего настроения.\n\n"\
                         "Нажми кнопку ниже и выбери, что конкретно ты хочешь мне отправить!",
                         reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())