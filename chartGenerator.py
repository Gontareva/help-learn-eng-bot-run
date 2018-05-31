import config
from GChartWrapper import *

class ChartGenerator(object):
    def __init__(self, count):
        self.__count = count
        self.__chart = None

    def generate(self, list_of_values, name, chat_id):
        # http://code.google.com/apis/chart/#line_charts
        section = (self.__count, len(list_of_values))[len(list_of_values) < self.__count]
        old_section = section - config.count_for_progress
        history = list_of_values[-section:]
        g = LineXY([list(range(0, old_section)), list_of_values[:old_section],
                    list(range(old_section - 1, section)), history[old_section - 1:]])

        g.color("blue", "8B0000")
        g.size(600, 300)
        g.grid(10.0, 10.0, 1, 0)
        len_history = len(history)
        max_value = max(history)
        min_value = min(history)
        g.scale(0, len_history - 1, min_value, max_value, 0, len_history - 1, min_value, max_value)
        g.grid(10.0, 10.0, 1, 10)
        g.axes('r')
        g.axes.range(0, min_value, max_value)
        g.title(name + " rating fot the last 100 exercises")
        file = str(chat_id)
        g.save(file)
        return file + ".png"
