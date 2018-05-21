import pymongo
import mongoengine


class Database(object):
    def __init__(self):
        self.__db = mongoengine.connect(db="helpLearnEnglishDatabase", host="localhost", port=27017)
        self.__users = self.__db.users

    def save(self, ex):
        # self.__users.
        print("ok")
