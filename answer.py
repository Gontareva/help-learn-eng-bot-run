import random
from soundex import *


class Answer(object):
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
        self.answer = random.choice(select_by_value(dictionary, stemmer.stem(word)))
        return self


class AnswerHomophone(Answer):
    def create(self, word, dictionary):
        self.answer = random.choice(select_by_value(dictionary, Soundex().encode(word)))
        return self


class AnswerSameTag(Answer):
    def create(self, part_of_speech, tag, dictionary):
        self.answer = random.choice(dictionary.get(part_of_speech.get()).get(tag.get()))
        return self


def select_by_value(list, value):
    return [word for word, attribute in list if attribute == value]


# a = type(AnswerHomophone())
# print(a)