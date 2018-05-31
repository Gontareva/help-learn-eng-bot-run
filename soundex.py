import copy


class Soundex(object):
    def encode(self, word):
        word = self.normalize(word)
        word = word.lower()
        first_char = copy.copy(word)[0]
        part_word = word[1:]
        without_hw = remove_hw(part_word)
        code = [replace(w)[True] for w in list(first_char+without_hw)][1:]
        result_code = "".join(remove_dupl(code)).replace("0", "").replace("7", "")
        return first_char+result_code[:3]


    def normalize(self, text):
        if text.isalpha():
            return text
        return ''.join([c for c in text if c.isalpha()])

def replace(char):
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


def remove_hw(word):
    return word.replace("h", "").replace("w", "")


def remove_dupl(code):
    new_code = ["0"]
    for c in code:
        if new_code[len(new_code) - 1] != c:
            new_code.append(c)
    return new_code



#
# a = Soundex()
# print(a.create("Pfister"))


print(normalize("aw12'.g"))
