import os
from progressBar import *
from exercise import *
from tagMapping import *
from answer import *
from singleton import *
from text import *


class ExerciseGenerator(object):
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
        part_of_speech = random.choice(list_parts_of_speech)
        try:
            list_of_tagged_words = self.__text.find_sentence(part_of_speech, 5)
        except Exception as e:
            print("generate-- ", e)
            list_of_tagged_words = self.__text.find_sentence(part_of_speech, 5)
        word, tag = self.__select_word(list_of_tagged_words, part_of_speech)
        list_of_words = [word for word, _ in list_of_tagged_words]
        sent = " ".join(list_of_words).replace(word, "*_____*", 1)
        count_answers = level * 2 + 2
        answer_options = self.__create_answer_options(word=word, part_of_speech=part_of_speech, tag=tag,
                                                      count=count_answers)
        ex = Exercise(chat_id=chat_id, sentence=sent, answer=word, part_of_speech=part_of_speech.get(), level=level,
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
