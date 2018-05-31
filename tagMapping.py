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
