import nltk
from progressBar import *
from exercise import *
from tagMapping import *
from answer import *
from singleton import *


class ExerciseGenerator(Singleton, object):
    def __init__(self):
        self.__tag_mapping = TagMapping()

        prog = ProgressBar(total=60, bar_length=26, complete_symbol="=")
        prog.set_prefix("Загрузка:  ")

        prog.next(" Тегирование текста...")
        self.__tagged_words_dictionary = nltk.corpus.brown.tagged_words()

        prog.next(" Загрузка предложений...")
        self.__sents = nltk.corpus.brown.sents()

        prog.next(" Формирование словаря...")
        self.__dictionary = {}
        self.__load_words_by_part_of_speech()

        prog.next(" Стемминг слов...")
        self.__stemmer = nltk.stem.porter.PorterStemmer()
        self.__stem_dictionary = [(word, self.__stemmer.stem(word)) for word, _ in self.__tagged_words_dictionary]

        prog.next(" Кодирование слов методом Soundex...")
        self.__soundex_dictionary = [(word, Soundex().encode(word)) for word, _ in self.__tagged_words_dictionary]

        prog.next(" Успешная загрузка.")
        prog.end()

    # генерирование задания
    def generate(self, chat_id, level, part_of_speech_):
        part_of_speech = part_of_speech_.get()
        list_of_words = self.__find_sentence(part_of_speech_, 4)
        word, tag = self.__select_word(list_of_words, part_of_speech_)
        sent = " ".join(list_of_words).replace(word, "*_____*", 1)
        count_answers = level * 2 + 2
        answer_options = self.__create_answer_options(word=word, part_of_speech=part_of_speech_, tag=Tag(tag),
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
                answer = AnswerHomophone().create(word, self.__soundex_dictionary)
            else:
                answer = AnswerWordForm().create(word, self.__stem_dictionary, self.__stemmer)
            if not list_of_answers.count(answer):
                list_of_answers.append(answer)

        random.shuffle(list_of_answers)
        return [answer.get() for answer in list_of_answers]

    # поиск подходящего предложения
    def __find_sentence(self, part_of_speech, min_length):
        sent = []
        tagged_sent = nltk.pos_tag(sent)
        while len(sent) < min_length and not len(self.__select_by_part_of_speech(tagged_sent, part_of_speech)):
            sent = random.choice(self.__sents)
        return sent

    # выбор слов части речи part_of_speech
    def __select_by_part_of_speech(self, list, part_of_speech):
        tags = self.__tag_mapping.tags(part_of_speech.get())
        return [(word, tag) for word, tag in list if tags.count(tag) != 0]

    # формирование словаря - распределение слов по частям речи и тегам
    def __load_words_by_part_of_speech(self):
        for part_of_speech in self.__tag_mapping.parts_of_speech():
            self.__dictionary[part_of_speech] = {}
            for tag in self.__tag_mapping.tags(part_of_speech):
                self.__dictionary[part_of_speech][tag] = []
        for word, tag in self.__tagged_words_dictionary:
            part_of_speech = self.__tag_mapping.part_of_speech(tag)
            if part_of_speech:
                self.__dictionary[part_of_speech][tag].append(word)

    # выбор слова из предложения как ответ в составляемом задании
    def __select_word(self, sentence, part_of_speech):
        tagged_words = nltk.pos_tag(sentence)
        word_tag = self.__select_by_part_of_speech(tagged_words, part_of_speech)
        return random.choice(word_tag)
