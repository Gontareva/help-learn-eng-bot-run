import nltk
from exercises import Exercises
from soundex import Soundex
import random
import time
import pyprog


# import db


class CreatorExercises(object):
    def __init__(self):
        prog = pyprog.ProgressBar(" ", " ", total=70, bar_length=26, complete_symbol="=", not_complete_symbol=" ",
                                  wrap_bar_prefix=" [", wrap_bar_suffix="] ", progress_explain="",
                                  progress_loc=pyprog.ProgressBar.PROGRESS_LOC_END)
        # Update Progress Bar
        print("Загрузка:  ")
        prog.update()
        progress_bar(prog)
        self.__tagged_words_dictionary = nltk.corpus.brown.tagged_words(tagset='universal')
        progress_bar(prog)
        self.__sents = nltk.corpus.brown.sents()
        progress_bar(prog)
        # db_texts = db.Database().texts.find()
        # stt = []
        # for t in db_texts:
        #     print(t)
        #     ss = nltk.tokenize.sent_tokenize(t["text"])
        #     print(ss)
        #     st = []
        #     for w in ss:
        #         st.extend(nltk.tokenize.word_tokenize(w))
        #     stt.extend( nltk.pos_tag(st, tagset="universal"))
        #     print(stt)
        # self.__tagged_words_dictionary += stt
        # print(len(self.__tagged_words_dictionary))
        self.__noun_dictionary = select(self.__tagged_words_dictionary, "NOUN")
        progress_bar(prog)
        self.__stemmer = nltk.stem.porter.PorterStemmer()
        progress_bar(prog)
        self.__stem_dictionary = [(w[0], self.__stemmer.stem(w[0])) for w in self.__tagged_words_dictionary]
        progress_bar(prog)
        self.__soundex_dictionary = [(w[0], Soundex().create(w[0])) for w in self.__tagged_words_dictionary]
        progress_bar(prog)

        # self.__verb_dictionary = select_by_tag(self.__tagged_words_dictionary, "VERB")
        # self.__adj_dictionary = select_by_tag(self.__tagged_words_dictionary, "ADJ")
        # self.__adv_dictionary = select_by_tag(self.__tagged_words_dictionary, "ADV")
        # self.__pron_dictionary = select_by_tag(self.__tagged_words_dictionary, "PRON")
        print("Успешная загрузка")
        prog.end()

    def create(self, chat_id, tag):
        words = []
        if len(words) < 4:
            words = random.choice(self.__sents)
        word = '1'
        while not word.isalpha() or not word.islower():
            word = select_word(words, tag)
        sent_ex = words
        if word:
            i = sent_ex.index(word)
            sent_ex.pop(i)
            sent_ex.insert(i, "*_____*")
            sent = " ".join(sent_ex)
            answer_options = []
            i = 1
            answer_options.append(word)
            while len(sorted(set(answer_options))) < 4:
                r = random.choice([1, 2, 3])
                if r == 1:
                    w = random.choice(self.__noun_dictionary)
                elif r == 2:
                    w = random.choice(select(self.__soundex_dictionary, Soundex().create(word)))
                else:
                    w = random.choice(select(self.__stem_dictionary, self.__stemmer.stem(word)))
                answer_options.append(w)

            answer_options = sorted(set(answer_options))
            random.shuffle(answer_options)
            ex = Exercises(chat_id=chat_id, sentence=sent, answer=word, tag=tag,
                           answer_options=answer_options)
            return ex
        else:
            return None

        # генерирование вариантов ответа для теста

    def __create_answer_options(self):
        all_tagged_words = nltk.corpus.brown.tagged_words(tagset='universal')
        tagged_words = select(all_tagged_words, self.tag)
        length = len(tagged_words)
        tagged_words.append(self.answer)

        index = tagged_words.index(self.answer)
        sorted_words = nltk.FreqDist(tagged_words).most_common(length)

        if index != length:
            ind = [w[0] for w in sorted_words].index(self.answer)
            mod = length // 3
            level = ind // mod + 1
        else:
            level = 2
        most_common_words = sorted_words[:level * 100]
        words = [w[0] for w in most_common_words]

        self.answerOptions = random.sample(words, 3)
        self.level = level


def select_word(tokens, tag):
    # tokens = nltk.tokenize.word_tokenize(sentence)
    tagged_words = nltk.pos_tag(tokens, tagset='universal')
    words = select(tagged_words, tag)
    if words:
        return random.choice(words)
    else:
        return None


def select(words, object):
    return [w[0] for w in words if w[1] == object]


progress_stat = 0


def progress_bar(prog):
    global progress_stat
    for i in range(10):
        time.sleep(.1)
        progress_stat += 1
        prog.set_stat(progress_stat)
        prog.update()
