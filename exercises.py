import nltk
import random
from mongoengine import *


class Exercises(Document):
    message_id = IntField(required=True, min_value=1)
    chat_id = IntField(required=True, min_value=1)
    sentence = StringField(required=True, min_length=1)
    answer = StringField(required=True, min_length=1, max_length=50)
    level = IntField(required=True, min_value=1, max_value=3, default=1)
    tag = StringField(required=True, choices=["NOUN", "VERB", "ADV", "ADJ", "PRON"])
    answer_options = ListField(required=True, field=StringField(min_length=1, max_length=50))
    user_response = StringField(required=False, min_length=1)

    def print(self):
        print(self.message_id, self.sentence, self.answer, self.level, self.tag, self.answer_options,
              self.user_response)

    # def __init__(self, chat_id, message_id, sentence, answer, level, tag, answer_options):
    #     self.message_id = message_id
    #     self.chat_id = chat_id
    #     self.sentence = sentence
    #     self.answer = answer
    #     self.level = level
    #     self.tag = tag
    #     self.answer_options = answer_options
    #     self.user_response = ""

    def add_user_response(self, response):
        self.user_response = response
        return self

    # def to_json(self):
    #     dict_exercise = {"sentence": self.sentence, "answer" : self.answer, "level":self.level, "tag":self.tag,
    #                      "answer_options": self.answer_options, "user_response":self.user_response}
    #     return json.dumps(dict_exercise)
#
#     def create(self, words, tag):
#         word = select_word(words, tag)
#         sent = words
#         if word:
#             i = sent.index(word)
#             sent.pop(i)
#             sent.insert(i, "_____")
#             self.sentence = " ".join(sent)
#             self.answer = word
#             self.tag = tag
#             self.__create_answer_options()
#             return self
#         else:
#             return None
#
#     #
#     # def check(self, answer):
#     #     self.checked = self.answer == answer
#     #     return self.checked
#
#     def save(self):
#         exercise = (self.__db.find_one({"_id": self._id}),
#                     self.__db.find_one({"sentence": self.sentence, "answer": self.answer,
#                                         "level": self.level,
#                                         "tag": self.tag}))[self._id]
#         if not exercise:
#             self.__db.save({"sentence": self.sentence,
#                             "answer": self.answer,
#                             "level": self.level,
#                             "tag": self.tag,
#                             "answerOptions": self.answer_options}, {'unique': True})
#         else:
#             self._id = exercise["_id"]
#         return self
#
#     # def find_one(self,  id):
#     #     exercise = self._db.find_one({"_id": self._id})
#     #     self._id = exercise["_id"]
#     #     self.sentence = exercise["sentence"]
#     #     self.answer = exercise["answer"]
#     #     self.level = int(exercise["level"])
#     #     self.tag = exercise["tag"]
#     #     self.answerOptions = exercise["answerOptions"]
#
#     def print(self):
#         print("""sentence: {0},
# answer: {1},
# level: {2},
# tag: {3},
# answerOptions: {4}
# """
#               .format(self.sentence, self.answer, self.level, self.tag, self.answer_options))
#
#
# def select_word(tokens, tag):
#     # tokens = nltk.tokenize.word_tokenize(sentence)
#     tagged_words = nltk.pos_tag(tokens, tagset='universal')
#     words = select_by_tag(tagged_words, tag)
#     if words:
#         return random.choice(words)
#     else:
#         return None
#
#
# def select_by_tag(words, tag):
#     return [w[0] for w in words if w[1] == tag]
