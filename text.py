import nltk
import random


class Text(object):
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
