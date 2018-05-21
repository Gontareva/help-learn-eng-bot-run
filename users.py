from mongoengine import *
from exercises import Exercises


class Users(Document):
    chat_id = IntField(required=True, min_value=1, unique=True)
    name = StringField(required=False)
    progress = DecimalField(required=True, default=0, min_value=-2, max_value=101)
    level = IntField(required=True, min_value=0, max_value=3, default=1)
    tags = ListField(required=True, default=["NOUN"])
    repeat = BooleanField(required=True, default=True)
