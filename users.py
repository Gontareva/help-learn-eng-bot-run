from mongoengine import *
from exercises import Exercises


class Users(Document):
    chat_id = IntField(required=True, min_value=1, unique=True)
    progress = DecimalField(required=True, default=0, min_value=0, max_value=101)
    level = IntField(required=True, min_value=1, max_value=3, default=1)
    tags = ListField(required=True, default=["NOUN"])
    repeat = BooleanField(required=True, default=True)
    exercises = ListField(ReferenceField(Exercises), required=False, default=[])

    # meta={'collection':'users'}

