import config
import telebot
import datetime
from creatorExercises import CreatorExercises
from users import Users
from exercises import Exercises
from db import Database

bot = telebot.TeleBot(config.token)
creator = CreatorExercises()
db = Database()


@bot.message_handler(commands=['start'])
def start(message):
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

        sent_exercise(message)
    except Exception as e:
        print(e)


@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, "Общайся со мной кнопками.")
    print_info(message, "message:   " + message.text)


def sent_exercise(message):
    try:
        # if message.chat.id == 259603599:
        create_user(message)

        new_exercise = creator.create(message.chat.id, "NOUN")
        a = do_text(new_exercise)
        keyboard = do_keyboard(new_exercise)
        res = bot.send_message(chat_id=message.chat.id, text=a, reply_markup=keyboard, parse_mode='Markdown')
        new_exercise.message_id = res.message_id
        new_exercise.save()
        new_exercise.reload()

        ex = Users.objects(chat_id=message.chat.id)

        print_info(message, new_exercise.sentense)

        # else:
        #     bot.send_message(chat_id=message.chat.id, text="Напиши мне позже;)")
        #     print(message.from_user.first_name, message.from_user.last_name, message.from_user.username, message.text)
        #     assert bot.send_message('259603599',
        #                             str(datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S'))
        #                             + "----" + str(message.from_user.first_name) + str(message.from_user.last_name)
        #                             + " ->>>>> " + str(message.text))
    except Exception as e:
        print(e)


def do_keyboard(exercise):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in range(2):
        btn1 = telebot.types.InlineKeyboardButton(text=exercise.answer_options[i * 2],
                                                  callback_data=exercise.answer_options[i * 2])
        btn2 = telebot.types.InlineKeyboardButton(text=exercise.answer_options[i * 2 + 1],
                                                  callback_data=exercise.answer_options[i * 2 + 1])
        keyboard.row(btn1, btn2)
    keyboard.row(telebot.types.InlineKeyboardButton(text="Удалить ⬅️ ", callback_data="#delete"),
                 telebot.types.InlineKeyboardButton(text="Проверить ✅ ", callback_data="#check"))
    return keyboard


def do_keyboard_next():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(text="Настройки ⚙️️ ", callback_data="#settings"),
                 telebot.types.InlineKeyboardButton(text="Следующее задание ➡️ ", callback_data="#next"))
    return keyboard


def do_text(exercise):
    return '*Вставьте пропущенное в предложении слово:*\n\n' + exercise.sentence


def create_user(message):
    if not Users.objects(chat_id=message.chat.id).first():
        Users(chat_id=message.chat.id, name=message.from_user.first_name + " " + message.from_user.last_name).save()


def print_info(message, text):
    print(str(message.from_user.first_name) + " " + str(message.from_user.last_name)
          + " ->>>>> " + text)


@bot.callback_query_handler(func=lambda callback: True)
def inline(callback):
    try:
        exercise = Exercises.objects(message_id=callback.message.message_id,
                                     chat_id=callback.message.chat.id).first()
        user = Users.objects(chat_id=callback.message.chat.id).first()
        if type(exercise) is Exercises:
            if callback.data == "#delete":
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
                print_info(callback.message, callback.data)
            elif callback.data.startswith("#check"):
                if not exercise.check:
                    text = "*Ответ: *" + exercise.sentence.replace("_____",
                                                                   exercise.user_response) + "\n*Проверка:* " \
                           + exercise.sentence.replace("_____", exercise.answer) + "\n*Результат:* "
                    progress = user.progress
                    level = user.level
                    right = True
                    if exercise.answer == exercise.user_response:
                        text += "Задание выполнено верно ✅"
                        progress += 1
                        if progress > 100:
                            level += 1
                            progress = 0
                        if level > 3:
                            level = 3
                    else:
                        text += "Задание выполнено неверно ❌"
                        progress -= 1
                        if progress < 0:
                            level -= 1
                            progress = 0
                        if level <= 0:
                            level = 1
                        right = False

                    exercise.update(set__right=right, set__check=True)
                    user.update(set__level=level, set__progress=progress)
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
            elif callback.data == "#next":
                if exercise.check:
                    bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
                                                  message_id=callback.message.message_id,
                                                  reply_markup=[])
                    if exercise.right:
                        exercise.delete()
                    sent_exercise(callback.message)
                print_info(callback.message, callback.data)
            elif callback.data == "#settings":
                print_info(callback.message, callback.data)
                pass
            else:
                exercise = Exercises.objects(message_id=callback.message.message_id,
                                             chat_id=callback.message.chat.id).first()
                exercise.update(set__user_response=callback.data)
                bot.edit_message_text(chat_id=callback.message.chat.id,
                                      message_id=callback.message.message_id,
                                      text=do_text(exercise).replace("_____", callback.data),
                                      parse_mode='Markdown')
                keyboard = do_keyboard(exercise)
                bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                              reply_markup=keyboard)
                print_info(callback.message, "answer:       " + callback.data)
    except Exception as e:
        print(e)


def check_answer(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    try:
        print(bot.get_me())
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
