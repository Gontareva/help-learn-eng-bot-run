import random


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

    def crete(self, word):
        self.answer = word
        return self


class AnswerWordForm(Answer):
    def create(self, word, dictionary, stemmer):
        list_words = dictionary.get(stemmer.stemming(word))
        if len(list_words) != 0:
            self.answer = random.choice(list_words)
            return self
        self.answer = word
        return self


class AnswerHomophone(Answer):
    def create(self, word, dictionary, soundex):
        list_words = dictionary.get(soundex.encode(word))
        if len(list_words) != 0:
            self.answer = random.choice(list_words)
            return self
        self.answer = word
        return self


class AnswerSameTag(Answer):
    def create(self, part_of_speech, tag, dictionary):
        self.answer = random.choice(dictionary.get(part_of_speech.get()).get(tag.get()))
        return self

# a = type(AnswerHomophone())
# print(a)
