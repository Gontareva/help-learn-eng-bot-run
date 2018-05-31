from mongoengine import *


class Exercises(Document):
    message_id = IntField(required=True, min_value=1)
    chat_id = IntField(required=True, min_value=1)
    sentence = StringField(required=True, min_length=1)
    answer = StringField(required=True, min_length=1, max_length=50)
    level = IntField(required=True, min_value=1, max_value=3, default=1)
    tag = StringField(required=True, choices=["NOUN", "VERB", "ADV", "ADJ", "PRON"])
    answer_options = ListField(required=True, field=StringField(min_length=1, max_length=50))
    user_response = StringField(required=True, min_length=1, default="_____")
    right = BooleanField(required=True, default=False)
    check = BooleanField(required=True, default=False)

    def print(self):
        print(self.message_id, self.sentence, self.answer, self.level, self.tag, self.answer_options,
              self.user_response)

    def add_user_response(self, response):
        self.user_response = response
        return self
