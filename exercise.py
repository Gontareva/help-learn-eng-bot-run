from mongoengine import *
from tagMapping import *


class Exercise(Document):
    message_id = IntField(required=True, min_value=1)
    chat_id = IntField(required=True, min_value=1)
    sentence = StringField(required=True, min_length=1)
    answer = StringField(required=True, min_length=1, max_length=50)
    level = IntField(required=True, min_value=1, max_value=3, default=1)
    part_of_speech = StringField(required=True, choices=TagMapping().parts_of_speech())
    answer_options = ListField(required=True, field=StringField(min_length=1, max_length=50))
    user_response = StringField(required=True, min_length=1, default="_____")
    right = BooleanField(required=True, default=False)
    checked = BooleanField(required=True, default=False)
    closed = BooleanField(required=True, default=False)

    def add_user_response(self, response):
        self.user_response = response
        return self

    def check(self):
        return self.answer == self.user_response

    def print(self):
        print(self.message_id, self.sentence, self.answer, self.level, self.part_of_speech, self.answer_options,
              self.user_response)
