class Tag(object):
    def __init__(self, tag):
        self.__tag = tag

    def __eq__(self, other):
        return type(other) is Tag and self.__tag == other.__tag

    def __ne__(self, other):
        return not type(other) is Tag or self.__tag != other.__tag

    def get(self):
        return self.__tag


# a = Tag("noun")
# b = Tag("verb")
# print(a.get(), b.get())
