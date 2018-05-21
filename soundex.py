import copy


class Soundex(object):
    def create(self, word):
        if word.isalpha():
            word = word.lower()
            first_char = copy.copy(word)[0]
            part_word = word[1:]
            without_hw = self.__remove_hw(part_word)
            code = [self.__change(w)[True] for w in list(first_char+without_hw)][1:]
            result_code = "".join(self.__remove_dupl(code)).replace("0", "").replace("7", "")
            return first_char+result_code[:3]
        else:
            return "0000"

    def __change(self, char):
        # return {char == "b" or "p": "1",
        #         char == "f" or "v": "2",
        #         char == "c" or "k" or "s": "3",
        #         char == "g" or "j": "4",
        #         char == "q" or "x" or "z": "5",
        #         char == "d" or "t": "6",
        #         char == "l": "7",
        #         char == "m" or "n": "8",
        #         char == "r": "9"}
        return {
            "bpfv".find(char) != -1: "1",
            "cksgjqxz".find(char) != -1: "2",
            "dt".find(char) != -1: "3",
            char == "l": "4",
            "mn".find(char) != -1: "5",
            char == "r": "6",
            "aeiouy".find(char) != -1: "0",
            "hw".find(char) != -1: "7",
        }

    def __remove_hw(self, word):
        return word.replace("h", "").replace("w", "")

    def __remove_dupl(self, code):
        new_code = ["0"]
        for c in code:
            if new_code[len(new_code) - 1] != c:
                new_code.append(c)
        return new_code

#
# a = Soundex()
# print(a.create("Pfister"))
