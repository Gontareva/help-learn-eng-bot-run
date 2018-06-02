import mongoengine
from progressBar import *
from exercise import *
from answer import *
from text import *
import time
import pyprog
import os
import telebot
import random
import datetime
from user import User
from exercise import Exercise
from chartGenerator import *
from tagMapping import *
from stemmer import *


class Answer():
    # answer = ""
    def __init__(self, answer=None):
        if answer:
            self.answer = answer

    def __eq__(self, other):
        return isinstance(other, Answer) and self.answer.lower() == other.answer.lower()

    def __ne__(self, other):
        return not isinstance(other, Answer) or self.answer.lower() != other.answer.lower()

    def get(self):
        return self.answer


class AnswerWordForm(Answer):
    def create(self, word, dictionary, stemmer):
        list_words = dictionary.get(stemmer.stemming(word))
        if len(list_words) != 0:
            self.answer = random.choice(list_words)
            return self
        return Answer(word)


class AnswerHomophone(Answer):
    def create(self, word, dictionary, soundex):
        list_words = dictionary.get(soundex.encode(word))
        if len(list_words) != 0:
            self.answer = random.choice(list_words)
            return self
        return Answer(word)


class AnswerSameTag(Answer):
    def create(self, part_of_speech, tag, dictionary):
        self.answer = random.choice(dictionary.get(part_of_speech.get()).get(tag.get()))
        return self


class ChartGenerator():
    def __init__(self, count):
        self.__count = count
        self.__chart = None

    def generate(self, list_of_values, name, chat_id):
        # http://code.google.com/apis/chart/#line_charts
        section = (self.__count, len(list_of_values))[len(list_of_values) < self.__count]
        old_section = section - config.count_for_progress
        history = list_of_values[-section:]
        g = LineXY([list(range(0, old_section)), list_of_values[:old_section],
                    list(range(old_section - 1, section)), history[old_section - 1:]])

        g.color("blue", "8B0000")
        g.size(600, 300)
        g.grid(10.0, 10.0, 1, 0)
        len_history = len(history)
        max_value = max(history)
        min_value = min(history)
        g.scale(0, len_history - 1, min_value, max_value, 0, len_history - 1, min_value, max_value)
        g.grid(10.0, 10.0, 1, 10)
        g.axes('r')
        g.axes.range(0, min_value, max_value)
        g.title(name + " rating fot the last 100 exercises")
        file = str(chat_id)
        g.save(file)
        return file + ".png"


class Database():
    def __init__(self):
        self.__connect = mongoengine.connect(db="helpLearnEnglishDatabase", host="localhost", port=27017)


class Exercise(Document):
    message_id = IntField(required=True, min_value=1)
    chat_id = IntField(required=True, min_value=1)
    sentence = StringField(required=True, min_length=1)
    answer = StringField(required=True, min_length=1, max_length=50)
    level = IntField(required=True, min_value=1, max_value=3, default=1)
    part_of_speech = StringField(required=True, choices=TagMapping().parts_of_speech())
    answer_options = ListField(required=True, field=StringField(min_length=1, max_length=50))
    user_response = StringField(required=True, min_length=1, default="_____")
    right = BooleanField(required=True, default=False)
    checked = BooleanField(required=True, default=False)

    def add_user_response(self, response):
        self.user_response = response
        return self

    def check(self):
        return self.answer == self.user_response

    def print(self):
        print(self.message_id, self.sentence, self.answer, self.level, self.part_of_speech, self.answer_options,
              self.user_response)


class ExerciseGenerator():
    def __init__(self, tag_mapping, stemmer, soundex):
        prog = ProgressBar(total=50, bar_length=40, complete_symbol="=")
        prog.set_prefix("Загрузка:  ")

        self.__tag_mapping = tag_mapping
        self.__stemmer = stemmer
        self.__soundex = soundex

        prog.next(" Загрузка текста...")
        self.__text = Text(self.__tag_mapping)

        prog.next(" Формирование словаря...")
        self.__dictionary = self.__tag_mapping.mapping_words(self.__text.tagged_words())

        prog.next(" Стемминг слов...")
        self.__stem_dictionary = self.__stemmer.stemming_list(self.__text.words())

        prog.next(" Кодирование слов методом Soundex...")
        self.__soundex_dictionary = self.__soundex.encode_list(self.__text.words())

        prog.next(" Успешная загрузка.")
        prog.end()

    # генерирование задания
    def generate(self, chat_id, level, list_parts_of_speech):
        list_of_tagged_words, part_of_speech_ = self.__text.find_sentence(list_parts_of_speech, 4)
        part_of_speech = part_of_speech_.get()
        word, tag = self.__select_word(list_of_tagged_words, part_of_speech_)
        list_of_words = [word for word, _ in list_of_tagged_words]
        sent = " ".join(list_of_words).replace(word, "*_____*", 1)
        count_answers = level * 2 + 2
        answer_options = self.__create_answer_options(word=word, part_of_speech=part_of_speech_, tag=tag,
                                                      count=count_answers)
        ex = Exercise(chat_id=chat_id, sentence=sent, answer=word, part_of_speech=part_of_speech, level=level,
                      answer_options=answer_options)
        return ex

    # генерирование вариантов ответа для теста
    def __create_answer_options(self, word, part_of_speech, tag, count):
        list_of_answers = [Answer(word)]
        answer = Answer()
        while len(list_of_answers) < count:
            r = random.choice([1, 2, 3])
            if r == 1:
                answer = AnswerSameTag().create(part_of_speech, tag, self.__dictionary)
            elif r == 2:
                answer = AnswerHomophone().create(word, self.__soundex_dictionary, self.__soundex)
            else:
                answer = AnswerWordForm().create(word, self.__stem_dictionary, self.__stemmer)
            if not (answer in list_of_answers):
                list_of_answers.append(answer)

        random.shuffle(list_of_answers)
        return [answer.get() for answer in list_of_answers]

    # выбор слова из предложения как ответ в составляемом задании
    def __select_word(self, tagged_words, part_of_speech):
        tags = self.__tag_mapping.tags(part_of_speech.get())
        word_tag = [(word, tag) for word, tag in tagged_words if (tag in tags) and word.islower()]
        word, tag = random.choice(word_tag)
        return word, Tag(tag)


class PartOfSpeech():
    def __init__(self, name):
        self.__name = name

    def __eq__(self, other):
        return type(other) is PartOfSpeech and self.__name == other.__name

    def __ne__(self, other):
        return not type(other) is PartOfSpeech or self.__name != other.__name

    def get(self):
        return self.__name


class ProgressBar():
    def __init__(self, total, bar_length, complete_symbol):
        self.__state = 0
        self.__prog = pyprog.ProgressBar(" ", " ", total=total, bar_length=bar_length, complete_symbol=complete_symbol,
                                         not_complete_symbol=" ", wrap_bar_prefix=" [", wrap_bar_suffix="] ",
                                         progress_explain="", progress_loc=pyprog.ProgressBar.PROGRESS_LOC_END)

    def next(self, text=""):
        for i in range(10):
            time.sleep(.2)
            self.__state += 1
            self.__prog.set_stat(self.__state)
            self.__prog.set_suffix(text)
            self.__prog.update()

    def set_prefix(self, text=""):
        self.__prog.set_prefix(text)

    def end(self):
        self.__prog.end()


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class Soundex():
    __values = "01230120022455012623010202"

    def __init__(self, encoding_length=4):
        self.__encoding_length = encoding_length

    def encode(self, text):
        prev_char = ''
        text = self.normalize(text)
        if not len(text):
            return text
        builder = []
        builder.append(text[0])

        for ch in text[1:]:
            c = self.__values[ord(ch) - ord('A')]
            if c != '0' and c != prev_char:
                builder.append(c)
                prev_char = c

        code = "".join(builder) + "0" * self.__encoding_length
        return code[:self.__encoding_length]

    def normalize(self, text):
        if text.isalpha():
            return text.upper()
        return ''.join([c.upper() for c in text if c.isalpha()])

    def encode_list(self, words):
        dictionary = {}
        for word in words:
            code = self.encode(word)
            if dictionary.get(code):
                dictionary[code].append(word)
            else:
                dictionary[code] = [word]

        return dictionary


class Stemmer:
    def __init__(self):
        self.__stemmer = nltk.stem.porter.PorterStemmer()

    def stemming_list(self, words):
        stem_dictionary = {}

        for word in words:
            stem_word = self.stemming(word)
            if stem_dictionary.get(stem_word):
                stem_dictionary[stem_word].append(word)
            else:
                stem_dictionary[stem_word] = [word]

        return stem_dictionary

    def stemming(self, word):
        return self.__stemmer.stem(word)


class Tag():
    def __init__(self, tag):
        self.__tag = tag

    def __eq__(self, other):
        return type(other) is Tag and self.__tag == other.__tag

    def __ne__(self, other):
        return not type(other) is Tag or self.__tag != other.__tag

    def get(self):
        return self.__tag


class TagMapping(Singleton):
    def __init__(self):
        self.__map = map_for_tags

    def parts_of_speech(self):
        return [a for a in self.__map]

    def tags(self, part_of_speech):
        return [value for value in self.__map.get(part_of_speech)]

    def part_of_speech(self, tag):
        for part_of_speech, tags in self.__map.items():
            if tags.count(tag):
                return part_of_speech
        return None

    # формирование словаря - распределение слов по частям речи и тегам
    def mapping_words(self, tagged_words):
        dictionary = {}
        for part_of_speech in self.parts_of_speech():
            dictionary[part_of_speech] = {}
            for tag in self.tags(part_of_speech):
                dictionary[part_of_speech][tag] = []
        for word, tag in tagged_words:
            part_of_speech = self.part_of_speech(tag)
            if part_of_speech:
                dictionary[part_of_speech][tag].append(word)

        return dictionary


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


class TelegramBot():
    def start(self):
        try:
            print(bot.get_me())
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)


class Text():
    def __init__(self, tag_mapping):
        self.__tag_mapping = tag_mapping
        self.__words = nltk.corpus.brown.words()
        self.__tagged_sents = nltk.corpus.brown.tagged_sents()
        self.__tagged_words = nltk.corpus.brown.tagged_words()

    # поиск подходящего предложения
    def find_sentence(self, parts_of_speech, min_length):
        sent = []
        part_of_speech = random.choice(parts_of_speech)
        while len(sent) < min_length or not len(self.__select_by_part_of_speech(sent, part_of_speech)):
            sent = random.choice(self.__tagged_sents)
        return sent, part_of_speech

    def __select_by_part_of_speech(self, list, part_of_speech):
        tags = self.__tag_mapping.tags(part_of_speech.get())
        return [(word, tag) for word, tag in list if tag in tags]

    def words(self):
        return self.__words

    def tagged_words(self):
        return self.__tagged_words


class User(Document):
    chat_id = IntField(required=True, min_value=1, unique=True)
    name = StringField(required=False)
    progress = FloatField(required=True, default=0)
    level = IntField(required=True, min_value=0, max_value=3, default=1)
    parts_of_speech = ListField(required=True, default=["NOUN"])
    repeat = BooleanField(required=True, default=True)
    count_for_repeat = IntField(required=False, min_value=0, default=0)
    count_for_progress = IntField(required=True, min_value=0, default=0)
    count_exercises = IntField(required=True, min_value=0, default=0)
    history_progress = ListField(required=True, default=[0])

    def get_parts_of_speech(self):
        return [PartOfSpeech(word) for word in self.parts_of_speech]
