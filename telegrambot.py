import config
import os
import telebot
import random
import datetime
from exerciseGenerator import ExerciseGenerator
from user import User
from exercise import Exercise
from db import Database
from chartGenerator import *
from partOfSpeech import *
from tagMapping import *
from stemmer import *
from soundex import *

bot = telebot.TeleBot(config.token)
tag_mapping = TagMapping()
generator = ExerciseGenerator(tag_mapping, Stemmer(), Soundex())
db = Database()


@bot.message_handler(commands=['start'])
def command_start(message):
    try:
        bot.send_message(message.from_user.id,
                         'Привет, я рад, что ты со мной!!!'
                         'Скоро я выучу английский язык и поделюсь своими знаниями с тобой 😉')
        bot.send_message(259603599, "start ----" + str(
            datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')) + " ->>>>> " + str(
            message.from_user.id) + " ->>>>> " +
                         str(message.from_user.first_name) + str(message.from_user.last_name))
        create_user(message)
        create_and_send_exercise(message)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['settings'])
def set_settings(message):
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="Просмотреть настройки", callback_data="#show_settings"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Выбрать части речи для изучения", callback_data="#set_tags"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Выбрать режим выполнения заданий", callback_data="#set_repeat"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Вернуться к обучению", callback_data="#next"))

        bot.send_message(message.chat.id, "*Выберите действие:*", reply_markup=keyboard, parse_mode='Markdown')
    except Exception as e:
        print(e)


@bot.message_handler(commands=['restart'])
def create_and_send_exercise(message):
    try:
        user = create_user(message)
        new_exercise = generator.generate(message.chat.id, user.level, user.get_parts_of_speech())
        res = send_exercise(new_exercise)
        new_exercise.message_id = res.message_id
        new_exercise.save()
    except Exception as e:
        print(e)


def send_exercise(exercise):
    a = make_text_for_message(exercise)
    keyboard = make_keyboard(exercise)
    return bot.send_message(chat_id=exercise.chat_id, text=a, reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, "Общайся со мной кнопками.")
    print_info(message, "message:   " + message.text)


def delete(exercise, message):
    if exercise.user_response != "_____":
        exercise.update(set__user_response="_____")

        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text=make_text_for_message(exercise),
                              parse_mode='Markdown')
        keyboard = make_keyboard(exercise)
        bot.edit_message_reply_markup(chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      reply_markup=keyboard)


def check_exercise(exercise, user, message):
    text = "*Ответ: *" + exercise.sentence.replace("_____", exercise.user_response) + \
           "\n*Проверка:* " + exercise.sentence.replace("_____", exercise.answer) + \
           "\n*Результат:* "
    progress = user.progress
    level = user.level
    right = True
    if exercise.check():
        text += "Задание выполнено верно ✅"
        progress += 1.0
        if progress > 100:
            level += 1
            progress = 0
            if level > 3:
                level = 3
    else:
        text += "Задание выполнено неверно ❌"
        right = False
        progress -= 1.0
        if progress < 0:
            level -= 1
            progress = 0
            if level <= 0:
                level = 1

    exercise.update(set__right=right, set__checked=True)
    user.update(set__level=level, set__progress=progress, inc__count_for_progress=1,
                inc__count_exercises=1, push__history_progress=progress)
    text += "\n*Рейтинг:* " + str(int(progress)) + "%\n*Уровень*: " + str(level)

    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=text,
                          parse_mode='Markdown')
    keyboard = make_keyboard_next()
    bot.edit_message_reply_markup(chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=keyboard)
    print_info(message, "#check    " + str(right))


def next(exercise, user, message):
    bot.edit_message_reply_markup(chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=[])
    if exercise.right:
        exercise.delete()
    if user.count_for_progress == config.count_for_progress:
        send_progress(user)
        user.update(set__count_for_progress=0)
    if user.count_for_repeat == config.count_for_repeat:
        send_repeat_exercise(message)
        user.update(set__count_for_repeat=0)
    else:
        create_and_send_exercise(message)
        user.update(inc__count_for_repeat=1)
    if len(user.history_progress) >= 100:
        user.update(pull__history_progress=0)
    # print_info(callback.message, data)


@bot.callback_query_handler(func=lambda callback: True)
def inline_query(callback):
    try:
        data = callback.data
        exercise = Exercise.objects(message_id=callback.message.message_id,
                                    chat_id=callback.message.chat.id).first()
        user = User.objects(chat_id=callback.message.chat.id).first()
        if type(exercise) is Exercise:
            if data.startswith("#delete"):
                delete(exercise, callback.message)
            elif data.startswith("#check"):
                if not exercise.checked:
                    check_exercise(exercise, user, callback.message)
            elif data.startswith("#next"):
                next(exercise, user, callback.message)
            elif data.startswith("#settings"):
                print_info(callback.message, data)
                set_settings(callback.message)
            elif data.startswith("#return_to_training"):
                create_and_send_exercise(callback.message)
            else:
                exercise.update(set__user_response=data)
                keyboard = make_keyboard(exercise)
                bot.edit_message_text(chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id,
                                      text=make_text_for_message(exercise, data),
                                      parse_mode='Markdown', reply_markup=keyboard)

                # print_info(callback.message, "answer:       " + data)
    except Exception as e:
        print(e)


def make_keyboard(exercise):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in range(len(exercise.answer_options) // 2):
        btn1 = telebot.types.InlineKeyboardButton(text=exercise.answer_options[i * 2],
                                                  callback_data=exercise.answer_options[i * 2])
        btn2 = telebot.types.InlineKeyboardButton(text=exercise.answer_options[i * 2 + 1],
                                                  callback_data=exercise.answer_options[i * 2 + 1])
        keyboard.row(btn1, btn2)
    keyboard.row(
        telebot.types.InlineKeyboardButton(text="Удалить ⬅️ ", callback_data="#delete"),
        telebot.types.InlineKeyboardButton(text="Проверить ✅ ",
                                           callback_data="#check"))
    return keyboard


def make_keyboard_next():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text="Настройки ⚙️️ ", callback_data="#settings"),
                 telebot.types.InlineKeyboardButton(text="Следующее задание ➡️ ", callback_data="#next"))
    return keyboard


def make_text_for_message(exercise, response=None):
    text = '*Вставьте пропущенное в предложении слово:*\n' + exercise.sentence
    if response:
        return text.replace("_____", response)
    return text


def create_user(message):
    user = User.objects(chat_id=message.chat.id).first()
    if not user:
        return User(chat_id=message.chat.id,
                    name=get_user_name(message.from_user)).save()
    return user


def get_user_name(user):
    name = ""
    if not (type(user.first_name) is str) and not (type(user.last_name) is str) and type(user.username) is str:
        name = user.username
    else:
        if type(user.first_name) is str:
            name += user.first_name
        name += " "
        if type(user.last_name) is str:
            name += user.last_name
    return name


def print_info(message, text):
    print(str(message.from_user.first_name) + " " + str(message.from_user.last_name)
          + " ->>>>> " + text)


def send_repeat_exercise(message):
    exercises = Exercise.objects(chat_id=message.chat.id)
    if len(exercises) > 0:
        repeat_exercise = random.choice(exercises)
        res = send_exercise(repeat_exercise)
        repeat_exercise.update(set__message_id=res.message_id, set__checked=False)
        repeat_exercise.reload()
    else:
        create_and_send_exercise(message)


def send_progress(user):
    file = ChartGenerator(100).generate(user.history_progress, user.name, user.chat_id)
    bot.send_photo(user.chat_id, open(file, 'rb'))
    os.remove(file)


def start():
    try:
        print(bot.get_me())
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
