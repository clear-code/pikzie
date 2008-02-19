class Color(object):
    names = ["black", "red", "green", "yellow",
             "blue", "magenta", "cyan", "white"]
    def __init__(self, name, foreground=True, intensity=False,
                 bold=True, italic=False, underline=False):
        self.name = name
        self.foreground = foreground
        self.intensity = intensity
        self.bold = bold
        self.italic = italic
        self.underline = underline

    def escape_sequence(self):
        sequence = []
        if self.name == "reset":
            sequence.append("0")
        else:
            if self.foreground:
                foreground_parameter = 3
            else:
                foreground_parameter = 4
            if self.intensity:
                foreground_parameter += 6
            sequence.append("%d%d" % (foreground_parameter,
                                      self.names.index(self.name)))
        if self.bold:
            sequence.append("1")
        if self.italic:
            sequence.append("3")
        if self.underline:
            sequence.append("4")
        return "\033[%sm" % ";".join(sequence)
    escape_sequence = property(escape_sequence)

    def __add__(self, other):
        return Color("%s:%s" % (self.name, other.name),
                     self.escape_sequence + other.escape_sequence)

COLORS = {
    "red": Color("red"),
    "red-back": Color("red", foreground=False),
    "green": Color("green"),
    "green-back": Color("green", foreground=False),
    "yellow": Color("yellow"),
    "blue": Color("blue"),
    "magenta": Color("magenta"),
    "cyan": Color("cyan"),
    "white": Color("white"),
    "white-back": Color("white", foreground=False),
    "reset": Color("reset", bold=False),
    }
