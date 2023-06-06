from aiogram import Dispatcher, types


async def start(message: types.Message):
    message_text = """Hi, I'm a bot, to start guess number game write '/guess'"""
    await message.reply(message_text)

def setup(dp: Dispatcher):
    dp.register_message_handler(start, content_types=['text'], state='*', commands=['start'])
