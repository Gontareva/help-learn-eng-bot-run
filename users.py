from mongoengine import *


class Users(Document):
    chat_id = IntField(required=True, min_value=1, unique=True)
    name = StringField(required=False)
    progress = FloatField(required=True, default=0)
    level = IntField(required=True, min_value=0, max_value=3, default=1)
    tags = ListField(required=True, default=["NOUN"])
    repeat = BooleanField(required=True, default=True)
    count_for_repeat = IntField(required=False, min_value=0, default=0)
    count_for_progress = IntField(required=True, min_value=0, default=0)
    count_exercises = IntField(required=True, min_value=0, default=0)
    history_progress = ListField(required=True, default=[0])
