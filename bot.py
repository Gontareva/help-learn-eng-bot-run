import os
import telebot
import random
import datetime
from exerciseGenerator import ExerciseGenerator
from user import User
from exercise import Exercise
from db import Database
from chartGenerator import *
from tagMapping import *
from stemmer import *
from soundex import *

bot = telebot.TeleBot(config.token)
tag_mapping = TagMapping()
generator = ExerciseGenerator(tag_mapping, Stemmer(), Soundex())
db = Database()

parse_mode = "Markdown"
map_for_parts_of_speech_ = map_for_parts_of_speech
max_level = 3


class Bot(object):
    def start(self):
        pass


@bot.message_handler(commands=['start'])
def command_start(message):
    try:
        bot.send_message(message.from_user.id,
                         'Привет, мы рады, что ты с нами!\n'
                         'Этот бот поможет улучшить твои знания в английском языке 😉')
        bot.send_message(259603599, "start ----" + str(
            datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')) + " ->>>>> " + str(
            message.from_user.id) + " ->>>>> " +
                         str(message.from_user.first_name) + str(message.from_user.last_name))
        user = create_user(message)
        close_exercise(user)
        create_and_send_exercise(message)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['help'])
def help(message):
    try:
        bot.send_message(message.from_user.id,
                         'Этот бот предназначен для изучения английского языка.\n\n'
                         'Существует три уровня сложности заданий, каждый следующий сложнее предыдущего.\n'
                         'В задании необходимо нажатием кнопки заполнить подходящим словом пробел в предложении.\n'
                         'При желании можно изменить ответ или удалить его.\n'
                         'Кнопка "Проверить" завершит выполнение задания.\n\n'
                         'Комманда /settings - поможет изменить настройки бота.\n\n'
                         'Управлять ботом можно только с помощью кнопок и команд.\n\n'
                         'Удачи 🍀')
    except Exception as e:
        print(e)


@bot.message_handler(commands=['settings'])
def settings(message, mode="send"):
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text="Просмотреть настройки", callback_data="#show_settings"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Выбрать части речи для изучения",
                                               callback_data="#set_parts_of_speech"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Выбрать режим выполнения заданий", callback_data="#set_repeat"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Изменить уровень сложности заданий", callback_data="#set_level"))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text="Вернуться к обучению ➡️ ", callback_data="#return_to_training"))
        text_ = "*Выберите действие:*"
        if mode.startswith("send"):
            bot.send_message(chat_id=message.chat.id,
                             text=text_,
                             reply_markup=keyboard,
                             parse_mode=parse_mode)
        elif mode.startswith("edit"):
            bot.edit_message_text(chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  text=text_,
                                  reply_markup=keyboard,
                                  parse_mode=parse_mode)
    except Exception as e:
        print(e)


# @bot.message_handler(commands=['restart'])
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
    text_ = make_text_for_message(exercise)
    keyboard = make_keyboard(exercise)
    return bot.send_message(chat_id=exercise.chat_id, text=text_, reply_markup=keyboard, parse_mode=parse_mode)


@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, "Общайся со мной кнопками.")
    print_info(User.objects(chat_id = message.chat.id).first(), "message:   " + message.text)


def delete(exercise, message):
    if exercise.user_response != "_____":
        exercise.update(set__user_response="_____")

        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=message.message_id,
                              text=make_text_for_message(exercise),
                              parse_mode=parse_mode)
        keyboard = make_keyboard(exercise)
        bot.edit_message_reply_markup(chat_id=message.chat.id,
                                      message_id=message.message_id,
                                      reply_markup=keyboard)


def check_exercise(exercise, user, message):
    text_ = "*Ответ: *" + exercise.sentence.replace("_____", exercise.user_response) + \
            "\n*Проверка:* " + exercise.sentence.replace("_____", exercise.answer) + \
            "\n*Результат:* "
    progress = user.progress
    level = user.level
    right = True
    update_progress = (1.0, 0.5)[user.progress > 70.0]
    if exercise.check():
        text_ += "Задание выполнено верно ✅"
        progress += update_progress
        if progress > 100:
            level += 1
            progress = 0
            if level > 3:
                level = 3
    else:
        text_ += "Задание выполнено неверно ❌"
        right = False
        progress -= update_progress
        if progress < 0:
            level -= 1
            progress = 0
            if level <= 0:
                level = 1

    exercise.update(set__right=right, set__checked=True, set__closed=True)
    user.update(set__level=level, set__progress=progress, inc__count_for_progress=1,
                inc__count_exercises=1, push__history_progress=progress)
    text_ += "\n*Рейтинг:* " + str(int(progress)) + "%\n*Уровень*: " + str(level)

    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=text_,
                          parse_mode=parse_mode)
    keyboard = make_keyboard_next()
    bot.edit_message_reply_markup(chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  reply_markup=keyboard)
    print_info(user, "#check    " + str(right))


def next(user, message, exercise=None):
    delete_keyboard(message.message_id, message.chat.id)

    if exercise:
        exercise.update(set__closed=True)
        if exercise.right:
            exercise.delete()
    else:
        close_exercise(user)

    if user.count_for_progress >= config.count_for_progress:
        send_progress(user)
        user.update(set__count_for_progress=0)
    if user.count_for_repeat >= config.count_for_repeat:
        send_repeat_exercise(message)
        user.update(set__count_for_repeat=0)
    else:
        create_and_send_exercise(message)
        user.update(inc__count_for_repeat=1)
    if len(user.history_progress) >= 100:
        user.update(pull__history_progress=0)
    # print_info(callback.message, data)


def close_exercise(user):
    for exercise_ in Exercise.objects(chat_id=user.chat_id, closed=False):
        delete_keyboard(exercise_.message_id, exercise_.chat_id)
        exercise_.update(set__closed=True)


@bot.callback_query_handler(func=lambda callback: True)
def inline_query(callback):
    try:
        data = callback.data
        exercise = Exercise.objects(message_id=callback.message.message_id,
                                    chat_id=callback.message.chat.id).first()
        user = User.objects(chat_id=callback.message.chat.id).first()
        if exercise:
            if data.startswith("#delete"):
                delete(exercise, callback.message)
            elif data.startswith("#check"):
                if not exercise.checked:
                    check_exercise(exercise, user, callback.message)
            elif data.startswith("#next"):
                next(user, callback.message, exercise)
            elif data.startswith("#settings"):
                delete_keyboard(exercise.message_id, exercise.chat_id)
                settings(callback.message, "send")
            # elif data.startswith("#to_settings"):
            #     settings(callback.message, "edit")

            # elif data.startswith("#return_to_training"):
            #     next(user, callback.message)
            else:
                exercise.update(set__user_response=data)
                keyboard = make_keyboard(exercise)
                bot.edit_message_text(chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id,
                                      text=make_text_for_message(exercise, data),
                                      parse_mode=parse_mode,
                                      reply_markup=keyboard)
        else:
            if data.startswith("#to_settings"):
                settings(callback.message, "edit")
            elif data.startswith("#show_settings"):
                show_settings(callback.message, user)
            elif data.startswith("#return_to_training"):
                next(user, callback.message)
            elif data.startswith("#set_parts_of_speech"):
                set_parts_of_speech(user, callback.message)
            elif data.startswith("#part_of_speech"):
                _, part_of_speech = data.split(" ")
                update_users_parts_of_speech(part_of_speech, user)
                user.reload()
                set_parts_of_speech(user, callback.message)
            elif data.startswith("#set_repeat"):
                set_repeat(user, callback.message)
            elif data.startswith("#repeat"):
                _, answer = data.split(" ")
                set_repeat(user, callback.message, answer)
            elif data.startswith("#set_level"):
                set_level(user, callback.message)
            elif data.startswith("#level"):
                _, answer = data.split(" ")
                set_level(user, callback.message, answer)

        print_info(user, "answer:       " + data)
    except Exception as e:
        print(e)


def set_level(user, message, answer=None):
    text_ = "*Уровень сложности заданий: *"
    if answer:
        user.update(set__level=int(answer))
        user.reload()
    text_ += str(user.level)
    keyboard = telebot.types.InlineKeyboardMarkup()
    row = keyboard.row()
    for value in range(1, max_level + 1):
        row.add(telebot.types.InlineKeyboardButton(text=str(value),
                                                   callback_data="#level " + str(value)))
    keyboard_settings_next(keyboard)
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=text_,
                          parse_mode=parse_mode,
                          reply_markup=keyboard)


def set_repeat(user, message, answer=None):
    text_ = "*Повторять неверно выполненные задания: *"
    if answer:
        answer_bool = answer == "yes"
        user.update(set__repeat=answer_bool)
        user.reload()
    text_ += yes_or_no(user.repeat)
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text="Да",
                                                    callback_data="#repeat yes"),
                 telebot.types.InlineKeyboardButton(text="Нет",
                                                    callback_data="#repeat no")
                 )
    keyboard_settings_next(keyboard)

    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=text_,
                          parse_mode=parse_mode,
                          reply_markup=keyboard)


# Не работает
def set_parts_of_speech(user, message):
    list_ = translate_parts_of_speech(user.parts_of_speech)
    text_ = "*Части речи, выбранные для изучения: *\n\n     • " + " \n     • ".join(
        list_)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for part_of_speech in map_for_parts_of_speech_.items():
        keyboard.add(telebot.types.InlineKeyboardButton(text=translate_parts_of_speech([part_of_speech[0]])[0],
                                                        callback_data="#part_of_speech " + part_of_speech[0]))
    keyboard_settings_next(keyboard)
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=text_,
                          parse_mode=parse_mode,
                          reply_markup=keyboard)


def update_users_parts_of_speech(part_of_speech, user):
    if not (part_of_speech in user.parts_of_speech):
        user.update(push__parts_of_speech=part_of_speech)
    else:
        user.update(pull__parts_of_speech=part_of_speech)
        user.reload()
        if not len(user.parts_of_speech):
            user.update(push__parts_of_speech="NOUN")


def keyboard_settings_next(keyboard):
    keyboard.add(telebot.types.InlineKeyboardButton(text="Вернуться к настройкам ⚙️️ ", callback_data="#to_settings"))
    keyboard.add(
        telebot.types.InlineKeyboardButton(text="Вернуться к обучению ➡️ ", callback_data="#return_to_training"))


def show_settings(message, user):
    text_ = "*Имя пользователя: *" + user.name + "\n" + \
            "*Уровень: *" + str(user.level) + "\n" + \
            "*Рейтинг: *" + str(int(user.progress)) + "%\n" + \
            "*Части речи, выбранные для изучения: *" + ", ".join(
        translate_parts_of_speech(user.parts_of_speech)) + "\n" + \
            "*Повторять неверно выполненные задания: *" + yes_or_no(user.repeat) + "\n" + \
            "*Количество выполненных заданий: *" + str(user.count_exercises) + "\n"
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard_settings_next(keyboard)
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=message.message_id,
                          text=text_,
                          parse_mode=parse_mode,
                          reply_markup=keyboard)


def yes_or_no(value):
    return ("Нет", "Да")[value]


def translate_parts_of_speech(parts_of_speech):
    return [map_for_parts_of_speech_[value]["eng"] + "(" + map_for_parts_of_speech_[value]["ru"] + ")" for value in
            parts_of_speech]


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
    text_ = '*Вставьте пропущенное в предложении слово:*\n' + exercise.sentence
    if response:
        return text_.replace("_____", response)
    return text_


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


def print_info(user, text_):
    print(user.name + " " + str(user.chat_id) + " ->>>>> " + text_)


def send_repeat_exercise(message):
    exercises = Exercise.objects(chat_id=message.chat.id)
    if len(exercises) > 0:
        repeat_exercise = random.choice(exercises)
        res = send_exercise(repeat_exercise)
        repeat_exercise.update(set__message_id=res.message_id, set__checked=False, set__closed=False)
        repeat_exercise.reload()
    else:
        create_and_send_exercise(message)


def send_progress(user):
    file = ChartGenerator(100).generate(user.history_progress, user.name, user.chat_id, user.level)
    bot.send_photo(user.chat_id, open(file, 'rb'))
    os.remove(file)


def delete_keyboard(message_id, chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()

    bot.edit_message_reply_markup(chat_id=chat_id,
                                  message_id=message_id,
                                  reply_markup=keyboard)


class TelegramBot(Bot, object):
    def start(self):
        try:
            print(bot.get_me())
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
