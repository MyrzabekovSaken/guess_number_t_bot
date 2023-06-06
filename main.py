from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types, executor
import json
import random
import logging
from dotenv import load_dotenv
import os
logging.basicConfig(level=logging.INFO)

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("No API token provided")
else:
    print("Api token is successfully loaded")


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def load_scores():
    try:
        with open('scores.json', 'r') as file:
            scores = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        scores = {}
    return scores


def save_scores(scores):
    with open('scores.json', 'w') as file:
        json.dump(scores, file)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Hi, I'm a bot, to start guess number game write '/guess")


@dp.message_handler(commands=['guess'])
async def guess(message: types.Message):
    scores = load_scores()
    user_id = str(message.from_user.id)
    if user_id not in scores:
        scores[user_id] = {"score": 0, "attempts": 3}
        save_scores(scores)
        await message.reply("Welcome to the number guessing game! You have a score of 0 and you have 3 attempts to guess number.")

    number = random.randint(1, 10)
    await message.reply("Guess a number between 1 and 10.")

    await dp.current_state().set_data({'number': number})


@dp.message_handler()
async def guess_number(message: types.Message):
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
