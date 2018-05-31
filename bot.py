import config
import telebot
import datetime
from exerciseGenerator import ExerciseGenerator
from users import Users
from exercises import Exercises
from db import Database
import random
import os
from GChartWrapper import *

bot = telebot.TeleBot(config.token)
creator = ExerciseGenerator()
db = Database()


@bot.message_handler(commands=['start'])
def command_start(message):
    try:
        print_info(message, 'start ' + str(message.from_user.id))
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
        # if message.chat.id == 259603599:
        user = create_user(message)

        new_exercise = creator.create(message.chat.id, user.level, "NOUN")
        res = send_exercise(new_exercise)
        new_exercise.message_id = res.message_id
        new_exercise.save()

        print_info(message, new_exercise.sentence)

        # else:
        #     bot.send_message(chat_id=message.chat.id, text="Напиши мне позже;)")
        #     print(message.from_user.first_name, message.from_user.last_name, message.from_user.username, message.text)
        #     assert bot.send_message('259603599',
        #                             str(datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'))
        #                             + "----" + str(message.from_user.first_name) + str(message.from_user.last_name)
        #                             + " ->>>>> " + str(message.text))
    except Exception as e:
        print(e)


def send_exercise(exercise):
    a = do_text(exercise)
    keyboard = do_keyboard(exercise)
    return bot.send_message(chat_id=exercise.chat_id, text=a, reply_markup=keyboard, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, "Общайся со мной кнопками.")
    print_info(message, "message:   " + message.text)


def do_keyboard(exercise):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in range(2):
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


def do_keyboard_next():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text="Настройки ⚙️️ ", callback_data="#settings"),
                 telebot.types.InlineKeyboardButton(text="Следующее задание ➡️ ", callback_data="#next"))
    return keyboard


def do_text(exercise):
    return '*Вставьте пропущенное в предложении слово:*\n' + exercise.sentence


def create_user(message):
    user = Users.objects(chat_id=message.chat.id).first()
    if not user:
        name = ''
        if not (type(message.from_user.first_name) is str) and not (type(message.from_user.last_name) is str) and type(
                message.from_user.username) is str:
            name = message.from_user.username
        else:
            if type(message.from_user.first_name) is str:
                name += message.from_user.first_name
            name += " "
            if type(message.from_user.last_name) is str:
                name += message.from_user.last_name
        return Users(chat_id=message.chat.id,
                     name=name).save()
    return user


def print_info(message, text):
    print(str(message.from_user.first_name) + " " + str(message.from_user.last_name)
          + " ->>>>> " + text)


@bot.callback_query_handler(func=lambda callback: True)
def inline(callback):
    try:
        data = callback.data
        exercise = Exercises.objects(message_id=callback.message.message_id,
                                     chat_id=callback.message.chat.id).first()
        user = Users.objects(chat_id=callback.message.chat.id).first()
        if type(exercise) is Exercises:
            if data.startswith("#delete"):
                if exercise.user_response != "_____":
                    exercise.update(set__user_response="_____")

                    bot.edit_message_text(chat_id=callback.message.chat.id,
                                          message_id=callback.message.message_id,
                                          text=do_text(exercise),
                                          parse_mode='Markdown')
                    keyboard = do_keyboard(exercise)
                    bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id,
                                                  reply_markup=keyboard)
                print_info(callback.message, data)
            elif data.startswith("#check"):
                if not exercise.check:
                    text = "*Ответ: *" + exercise.sentence.replace("_____",
                                                                   exercise.user_response) + "\n*Проверка:* " \
                           + exercise.sentence.replace("_____", exercise.answer) + "\n*Результат:* "
                    progress = user.progress
                    level = user.level
                    right = True
                    if exercise.answer == exercise.user_response:
                        text += "Задание выполнено верно ✅"
                        progress += 1.0
                        if progress > 100:
                            level += 1
                            progress = 0
                        if level > 3:
                            level = 3
                    else:
                        text += "Задание выполнено неверно ❌"
                        progress -= 1.0
                        if progress < 0:
                            level -= 1
                            progress = 0
                        if level <= 0:
                            level = 1
                        right = False

                    exercise.update(set__right=right, set__check=True)
                    user.update(set__level=level, set__progress=progress, inc__count_for_progress=1,
                                inc__count_exercises=1, push__history_progress=progress)
                    text += "\n*Рейтинг:* " + str(int(progress)) + "%\n*Уровень*: " + str(level)

                    bot.edit_message_text(chat_id=callback.message.chat.id,
                                          message_id=callback.message.message_id,
                                          text=text,
                                          parse_mode='Markdown')
                    keyboard = do_keyboard_next()
                    bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id,
                                                  reply_markup=keyboard)
                    print_info(callback.message, "#check    " + str(right))
            elif data.startswith("#next"):
                if exercise.check:
                    bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id,
                                                  reply_markup=[])
                    if exercise.right:
                        exercise.delete()
                    if user.count_for_progress == config.count_for_progress:
                        send_progress(user)
                        user.update(set__count_for_progress=0)
                    if user.count_for_repeat == config.count_for_repeat:
                        send_repeat_exercise(callback.message)
                        user.update(set__count_for_repeat=0)
                    if len(user.history_progress) >= 100:
                        user.update(pull__history_progress=0)
                    else:
                        create_and_send_exercise(callback.message)
                        user.update(inc__count_for_repeat=1)
                print_info(callback.message, data)
            elif data.startswith("#settings"):
                print_info(callback.message, data)
                set_settings(callback.message)
            elif data.startswith("#return_to_training"):
                create_and_send_exercise(callback.message)
            else:
                exercise = Exercises.objects(message_id=callback.message.message_id,
                                             chat_id=callback.message.chat.id).first()
                exercise.update(set__user_response=data)
                keyboard = do_keyboard(exercise)
                bot.edit_message_text(chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id,
                                      text=do_text(exercise).replace("_____", data),
                                      parse_mode='Markdown', reply_markup=keyboard)

                # print_info(callback.message, "answer:       " + data)
    except Exception as e:
        print(e)


def send_repeat_exercise(message):
    exercises = Exercises.objects(chat_id=message.chat.id)
    if len(exercises) > 0:
        repeat_exercise = random.choice(exercises)
        res = send_exercise(repeat_exercise)
        repeat_exercise.update(set__message_id=res.message_id, set__check=False)
        repeat_exercise.reload()
    else:
        create_and_send_exercise(message)


def check_answer(message):
    bot.send_message(message.chat.id, message.text)


def send_progress(user):
    # http://code.google.com/apis/chart/#line_charts
    count_100 = (100,len(user.history_progress))[len(user.history_progress)<100]
    count = count_100 - config.count_for_progress
    history = user.history_progress[-count_100:]
    G = LineXY([list(range(0, count)), user.history_progress[:count],
                list(range(count - 1, count_100)), history[count - 1:]])

    G.color("blue", "8B0000")
    G.size(600, 300)
    G.grid(10.0, 10.0, 1, 0)
    len_history = len(history)
    max_value = max(history)
    min_value = min(history)
    G.scale(0, len_history - 1, min_value, max_value, 0, len_history - 1, min_value, max_value)
    G.grid(10.0, 10.0, 1, 10)
    G.axes('r')
    G.axes.range(0, min_value, max_value)
    G.title(user.name + " rating fot the last 100 exercises")
    file = str(user.chat_id)
    G.save(file)
    file += ".png"
    bot.send_photo(user.chat_id, open(file, 'rb'))
    os.remove(file)


def start():
    try:
        print(bot.get_me())
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
