import mongoengine


class Database(object):
    def __init__(self):
        self.__connect = mongoengine.connect(db="helpLearnEnglishDatabase", host="localhost", port=27017)
