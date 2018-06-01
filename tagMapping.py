from singleton import *
from mapForTags import *
from partOfSpeech import *
from tag import *


class TagMapping(Singleton, object):
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

# a = TagMapping()
# b = TagMapping()
#
# print(a is b)


#
# dict = {}
#
# dict["a"]=["1","2"]
# dict["b"]={"11":["ggg"],"21":"0"}
# dict["b"]["11"].append("111")
#
# print(dict)
