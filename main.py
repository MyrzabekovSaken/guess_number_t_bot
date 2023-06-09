from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup 
import json
import random
import logging
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("No API token provided")
else:
    print("Api token is successfully loaded")

logging.basicConfig(level=logging.INFO)

def get_database():
    MONGO_URL = os.getenv("MONGO_URL")
    client = MongoClient(MONGO_URL)
    return client["test"]


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def load_scores():
    database = get_database()
    t_bot_result_collection = database["guess_number_result"]
    t_bot_document = t_bot_result_collection.find_one({})
    if t_bot_document:
        scores = t_bot_document.get("data", {})
    else:
        scores = {}
    return scores


def save_scores(scores):
    database = get_database()
    t_bot_result_collection = database["guess_number_result"]
    t_bot_result_collection.update_one({}, {"$set": {"data": scores}}, upsert=True)


@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.reply("Hi, I'm a bot, to start guess number game write '/guess")


@dp.message_handler(commands=['guess'])
async def guess(message: Message):
    scores = load_scores()
    user_id = str(message.from_user.id)
    if user_id not in scores:
        scores[user_id] = {"score": 0, "attempts": 3}
        save_scores(scores)
    await message.answer("Welcome to the number guessing game! You have a score of 0 and you have 3 attempts to guess number.")
        
    number = random.randint(1, 10)
    await message.answer("Guess a number between 1 and 10.")

    await dp.current_state().set_data({'number': number})


@dp.message_handler()
async def guess_number(message: Message):
    scores = load_scores()
    user_id = str(message.from_user.id)
    state = dp.current_state(user=user_id)
    data = await state.get_data()
    number = data.get('number')

    try:
        guess = int(message.text)
    except ValueError:
        await message.reply("Invalid input. Please enter a number.")
        return

    if guess < number:
        scores[user_id]['attempts'] -= 1
        await message.reply(f"Too low! Try again. You have {scores[user_id]['attempts']} attempts left.")
    elif guess > number:
        scores[user_id]['attempts'] -= 1
        await message.reply(f"Too high! Try again. You have {scores[user_id]['attempts']} attempts left.")
    else:
        scores[user_id]['score'] += 1
        save_scores(scores)
        await state.reset_state()
        await message.reply(f"Congratulations! You guessed the number. Your total score is {scores[user_id]['score']}.")
        await message.reply("If you want to play this game again go to '/guess'")

    if scores[user_id]['attempts'] == 0:
        await state.reset_state()
        await message.reply("Game over! You have no more attempts. Start a new game with '/guess'.")
        scores[user_id] = {'score': 0, 'attempts': 3}

    save_scores(scores)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    dbname = get_database()
    result = dbname["guess_number_result"]
