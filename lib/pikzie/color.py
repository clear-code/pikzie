# Copyright (C) 2009  Kouhei Sutou <kou@clear-code.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    "black": Color("black", bold=True),
    "black-back": Color("black", foreground=False),
    "red": Color("red", bold=True),
    "red-back": Color("red", foreground=False),
    "green": Color("green", bold=True),
    "green-back": Color("green", foreground=False),
    "yellow": Color("yellow", bold=True),
    "blue": Color("blue", bold=True),
    "magenta": Color("magenta", bold=True),
    "magenta-back": Color("magenta", foreground=False),
    "cyan": Color("cyan", bold=True),
    "cyan-back": Color("cyan", foreground=False),
    "white": Color("white", bold=True),
    "white-back": Color("white", foreground=False),
    "reset": Color("reset"),
    }

SCHEMES = {
    "default": {
        "success": COLORS["green"],
        "notification": COLORS["cyan"],
        "pending": COLORS["magenta"],
        "omission": COLORS["white-back"] + COLORS["blue"],
        "failure": COLORS["red"],
        "error": COLORS["yellow"],
        "test-case-name": COLORS["green-back"] + COLORS["white"],
        "file-name": COLORS["cyan"],
        "line-number": COLORS["yellow"],
        "content": None,
        }
    }
