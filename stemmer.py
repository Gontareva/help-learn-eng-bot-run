import nltk


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
