import copy


class Soundex(object):
    __values = "01230120022455012623010202"

    def __init__(self, encoding_length=4):
        self.__encoding_length = encoding_length

    def encode(self, text):
        prev_char = ''
        text = self.normalize(text)
        if not len(text):
            return text
        builder = [text[0]]

        for ch in text[1:]:
            c = self.__values[ord(ch) - ord('A')]
            if c != '0' and c != prev_char:
                builder.append(c)
                prev_char = c

        code = "".join(builder) + "0" * self.__encoding_length
        return code[:self.__encoding_length]

    def normalize(self, text):
        if text.isalpha():
            return text.upper()
        return ''.join([c.upper() for c in text if c.isalpha()])

    def encode_list(self, words):
        dictionary = {}
        for word in words:
            code = self.encode(word)
            if dictionary.get(code):
                dictionary[code].append(word)
            else:
                dictionary[code] = [word]

        return dictionary

#
# a = Soundex()
# print(a.encode("Book"))
#
# print(a.encode("Greet"))
# print("Greet"[1:])
#
# print(Soundex().normalize("aw12'.g"))
