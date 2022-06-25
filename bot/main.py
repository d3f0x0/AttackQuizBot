import logging

from aiogram import Bot, Dispatcher, executor, types
from postgresDB import DataBase
import random
from dotenv import dotenv_values
from datetime import datetime
from typingBot import Quiz


logging.basicConfig(level=logging.INFO)

config = dotenv_values(".env")

TOKEN = config.get("TOKEN")
POSTGRES_NAME = config.get("POSTGRES_NAME")
POSTGRES_PASSWORD = config.get("POSTGRES_PASSWORD")
POSTGRES_PORT = config.get("POSTGRES_PORT")
POSTGRES_HOST = config.get("POSTGRES_HOST")
POSTGRES_DB = config.get("POSTGRES_DB")
GENERATE_DATA = config.get("GENERATE_DATA")


db = DataBase(dbname=POSTGRES_DB, user=POSTGRES_NAME, password=POSTGRES_PASSWORD,
              host=POSTGRES_HOST, port=POSTGRES_PORT)


if GENERATE_DATA == 'True':
    db.generate_data()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

list_techniques = ['TA0009. Collection', 'TA0011. Command and Control', 'TA0006. Credential Access',
                   'TA0005. Defense Evasion', 'TA0007. Discovery', 'TA0002. Execution', 'TA0010. Exfiltration',
                   'TA0040. Impact', 'TA0001. Initial Access', 'TA0008. Lateral Movement', 'TA0003. Persistence',
                   'TA0004. Privilege Escalation', 'TA0043. Reconnaissance', 'TA0042. Resource Development']


def generate_quiz(data: list) -> Quiz:
    """Get tuple from postgresDB.py which contains 4 lists with """
    question_id = random.randint(0, len(data) - 1)
    if len(data[question_id][2]) > 300:
        question = f"{data[question_id][2].split('.')[0]}"
    else:
        question = f"{data[question_id][2]}"
    correct_answer_name = data[question_id][1]
    correct_answer_mitre_id = data[question_id][0]
    answers = [correct_answer_name]
    for new_answer in data:
        if new_answer[1] not in answers:
            answers.append(new_answer[1])
    mix_answers = random.sample(answers, len(answers))
    correct_answer_mix_id = mix_answers.index(correct_answer_name)
    return Quiz(question=question, true_answer=correct_answer_mix_id, answers=mix_answers,
                mitre_id=correct_answer_mitre_id)


@dp.message_handler(commands=["start"])
async def start_bot(message: types.Message):
    await message.answer(f"Hi, {message.chat.first_name}. I'm help you learned MITRE ATT&CK. "
                         f"For started click /quiz")


@dp.message_handler(commands=["quiz"])
async def start_quiz(message: types.Message):
    technique_button = types.ReplyKeyboardMarkup(resize_keyboard=False, row_width=1)
    list_mode = ['Technique', 'Mitigations', 'Tactics']
    for button in list_mode:
        technique_button.add(types.KeyboardButton(text=button))
    db.insert_users(user_id=message.chat.id, user_name=message.chat.first_name, last_update=datetime.now())
    await message.answer('Choose quiz mode', reply_markup=technique_button)


@dp.message_handler(commands=["statistic"])
async def get_statistic(message: types.Message):
    stat = db.select_stat(message.chat.id)
    await message.answer(f"Dear, {message.chat.first_name} your true answers:\n "
                         f"Tactics: {stat.tactic}%\n"
                         f"Techniques: {stat.tech}%\n"
                         f"Mitigations: {stat.mitigations}%\n"
                         f"All stat: {stat.all_stat}%")


@dp.message_handler(regexp="^Technique$", content_types=['text'])
async def technique_choose(message: types.Message):
    technique_button = types.ReplyKeyboardMarkup(resize_keyboard=False, row_width=1)
    technique_button.add(types.KeyboardButton(text='From all tactics'))
    technique_button.add(types.KeyboardButton(text='Choose tactics'))
    await message.answer('Choose quiz mode', reply_markup=technique_button)


@dp.message_handler(regexp="^Mitigations$", content_types=['text'])
async def mitigations_quiz(message: types.Message):
    mitigations_all = db.select_mitigations()
    quiz = generate_quiz(data=mitigations_all)
    send_poll = await bot.send_poll(chat_id=message.chat.id, question=quiz.question, options=quiz.answers,
                                    allows_multiple_answers=False,
                                    correct_option_id=quiz.true_answer, open_period=30,
                                    type='quiz', explanation=quiz.answers[quiz.true_answer], is_anonymous=False)
    db.insert_stat(user_id=message.from_user.id, mitre_id=quiz.mitre_id,
                   true_poll_answer=quiz.true_answer,
                   poll_id=send_poll.poll.id)


@dp.message_handler(regexp="^From all tactics$", content_types=['text'])
async def technique_all(message: types.Message):
    techniques_all = db.select_techniques()
    quiz = generate_quiz(techniques_all)
    send_poll = await bot.send_poll(chat_id=message.chat.id, question=quiz.question, options=quiz.answers,
                                    allows_multiple_answers=False,
                                    correct_option_id=quiz.true_answer,
                                    type='quiz', explanation=quiz.answers[quiz.true_answer], open_period=30,
                                    is_anonymous=False)
    db.insert_stat(user_id=message.from_user.id, mitre_id=quiz.mitre_id,
                   true_poll_answer=quiz.true_answer,
                   poll_id=send_poll.poll.id)


@dp.message_handler(regexp="^Choose tactics$", content_types=['text'])
async def select_tactic_for_techniques(message: types.Message):
    technique_button = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    for technique in list_techniques:
        technique_button.add(types.KeyboardButton(text=technique))

    await message.answer('Choose quiz mode', reply_markup=technique_button)


@dp.message_handler(lambda message: message.text in list_techniques,
                    content_types=['text'])
async def select_techniques_one_tactics(message: types.Message):
    techniques_from_tactic = db.select_techniques(id_tactics=message.text.split('.')[0])
    quiz = generate_quiz(techniques_from_tactic)
    send_poll = await bot.send_poll(chat_id=message.chat.id, question=quiz.question, options=quiz.answers,
                                    allows_multiple_answers=False, open_period=30,
                                    correct_option_id=quiz.true_answer,
                                    type='quiz', explanation=quiz.answers[quiz.true_answer], is_anonymous=False)
    db.insert_stat(user_id=message.from_user.id, mitre_id=quiz.mitre_id,
                   true_poll_answer=quiz.true_answer,
                   poll_id=send_poll.poll.id)


@dp.message_handler(regexp="^Tactics$", content_types=['text'])
async def quiz_tactics(message: types.Message):
    all_tactics = db.select_tactics()
    quiz = generate_quiz(all_tactics)
    send_poll = await bot.send_poll(chat_id=message.chat.id, question=quiz.question, options=quiz.answers,
                                    allows_multiple_answers=False,
                                    correct_option_id=quiz.true_answer,
                                    type='quiz', explanation=quiz.answers[quiz.true_answer], is_anonymous=False,
                                    open_period=30)
    db.insert_stat(user_id=message.from_user.id, mitre_id=quiz.mitre_id,
                   true_poll_answer=quiz.true_answer,
                   poll_id=send_poll.poll.id)


@dp.poll_answer_handler()
async def some_poll_answer_handler(poll_answer: types.PollAnswer):
    db.update_stat(poll_answer=poll_answer.option_ids[0], poll_id=poll_answer.poll_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
