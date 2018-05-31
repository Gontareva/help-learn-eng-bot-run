class PartOfSpeech(object):
    def __init__(self, name):
        self.__name = name

    def __eq__(self, other):
        return type(other) is PartOfSpeech and self.__name == other.__name

    def __ne__(self, other):
        return not type(other) is PartOfSpeech or self.__name != other.__name

    def get(self):
        return self.__name