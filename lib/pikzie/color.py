class Color(object):
    def __init__(self, name, escape_sequence):
        self.name = name
        self.escape_sequence = escape_sequence

    def __add__(self, other):
        return Color("%s:%s" % (self.name, other.name),
                     self.escape_sequence + other.escape_sequence)

COLORS = {
    "red": Color("red", "\033[01;31m"),
    "red-back": Color("red-back", "\033[41m"),
    "green": Color("green", "\033[01;32m"),
    "green-back": Color("green-back", "\033[01;42m"),
    "yellow": Color("yellow", "\033[01;33m"),
    "blue": Color("blue", "\033[01;34m"),
    "purple": Color("purple", "\033[01;35m"),
    "cyan": Color("cyan", "\033[01;36m"),
    "white": Color("white", "\033[01;97m"),
    "white-back": Color("white-back", "\033[01;107m"),
    "normal": Color("normal", "\033[00m"),
    }
