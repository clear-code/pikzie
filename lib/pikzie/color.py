class Color(object):
    names = ["black", "red", "green", "yellow",
             "blue", "magenta", "cyan", "white"]
    def __init__(self, name, foreground=True, intensity=False,
                 bold=False, italic=False, underline=False):
        self.name = name
        self.foreground = foreground
        self.intensity = intensity
        self.bold = bold
        self.italic = italic
        self.underline = underline

    def sequence(self):
        sequence = []
        if self.name == "none":
            pass
        elif self.name == "reset":
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
        return sequence
    sequence = property(sequence)

    def escape_sequence(self):
        return "\033[%sm" % ";".join(self.sequence)
    escape_sequence = property(escape_sequence)

    def __add__(self, other):
        return MixColor([self, other])

class MixColor(object):
    def __init__(self, colors):
        self.colors = colors

    def sequence(self):
        return sum([color.sequence for color in self.colors], [])
    sequence = property(sequence)

    def escape_sequence(self):
        return "\033[%sm" % ";".join(self.sequence)
    escape_sequence = property(escape_sequence)

    def __add__(self, other):
        return MixColor([self, other])

COLORS = {
    "red": Color("red", bold=True),
    "red-back": Color("red", foreground=False),
    "green": Color("green", bold=True),
    "green-back": Color("green", foreground=False),
    "yellow": Color("yellow", bold=True),
    "blue": Color("blue", bold=True),
    "magenta": Color("magenta", bold=True),
    "cyan": Color("cyan", bold=True),
    "white": Color("white", bold=True),
    "white-back": Color("white", foreground=False),
    "reset": Color("reset"),
    }

SCHEMES = {
    "default": {
        "success": COLORS["green"],
        "notification": COLORS["cyan"],
        "pending": COLORS["magenta"],
        "failure": COLORS["red"],
        "error": COLORS["yellow"]
        }
    }
