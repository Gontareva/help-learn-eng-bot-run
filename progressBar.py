import time
import pyprog


class ProgressBar(object):
    def __init__(self, total, bar_length, complete_symbol):
        self.__state = 0
        self.__prog = pyprog.ProgressBar(" ", " ", total=total, bar_length=bar_length, complete_symbol=complete_symbol,
                                         not_complete_symbol=" ", wrap_bar_prefix=" [", wrap_bar_suffix="] ",
                                         progress_explain="", progress_loc=pyprog.ProgressBar.PROGRESS_LOC_END)

    def next(self, text=""):
        for i in range(10):
            time.sleep(.2)
            self.__state += 1
            self.__prog.set_stat(self.__state)
            self.__prog.set_suffix(text)
            self.__prog.update()

    def set_prefix(self, text=""):
        self.__prog.set_prefix(text)

    def end(self):
        self.__prog.end()