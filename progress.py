from GChartWrapper import *
import sys
import nltk


def send_progress(user=None):
    # http://code.google.com/apis/chart/#line_charts
    a = [0, 1.0, 2.0, 3.0, 2.0, 3.0, 4.0, 5.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 10.0, 11.0, 10.0]
    # h = int(100/len(a))
    # print(h)
    # print(list(range(0, 14 * h, h)))
    # print(list(range(13 * h, 19 * h, h)))
    # G = LineXY([list(range(0,14*h,h)), [0, 1.0, 2.0, 3.0, 2.0, 3.0, 4.0, 5.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], list(range(13*h, 19*h, h)), [9.0, 10.0, 11.0, 10.0, 11.0, 10.0]])
    print(list(range(0, 14)))
    print(list(range(13, 19)))
    # G = LineXY(
    #     [list(range(0, 14)), [0, 1.0, 2.0, 3.0, 2.0, 3.0, 4.0, 5.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], list(range(13, 19)),
    #      [9.0, 10.0, 11.0, 10.0, 11.0, 10.0]])
    print([a[:14], a[-6:]])
    G = LineXY([list(range(0, 14)), a[:14], list(range(13, 19)), a[-6:]])
    G.color("blue", "8B0000")
    G.size(600, 300)
    G.scale(0, len(a) - 1, min(a), max(a), 0, len(a) - 1, min(a), max(a))
    # G.scale(min(a), max(a))
    # G.scale(min(a), max(a))
    G.grid(10.0, 10.0, 1, 10)
    G.axes("rx")
    # last_value=10
    # max_value=11
    # G.axes.label(0, last_value)
    # G.axes.position(0, int(100 * last_value / max_value))  # 0 to 100
    G.axes.range(0, min(a) - 1, max(a))
    # G.title("I" + " rating fot the last 100 exercises")
    file = str(259603599)
    G.save(file)
    file += ".png"
    bot.send_photo(259603599, open(file, 'rb'))
    # os.remove(file)


import config
import telebot

# bot = telebot.TeleBot(config.token)
#
# @bot.message_handler(content_types=['text'])
# def text(message):
#     bot.send_photo(259603599, open('qqq.jpg', 'rb'))

if __name__ == '__main__':
    print(nltk.corpus.brown.tagged_sents())
    print(nltk.stem.porter.PorterStemmer().stem("book"))
    print(nltk.stem.porter.PorterStemmer().stem("booking"))

    # print("aaa1")
    # if 10:
    #     print(sys.version)
    # send_progress()
    # try:
    #     pass
    #     print(bot.get_me())
    #     bot.polling(none_stop=True)
    # except Exception as e:
    #     print(e)

    print("aaa")
