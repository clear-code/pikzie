import re

import pikzie
import test.utils

color = pikzie.color.Color
mix_color = pikzie.color.MixColor

class TestColor(pikzie.TestCase, test.utils.Assertions):
    """Tests for color."""

    def test_color_escape_sequence(self):
        self.assert_escape_sequence(["31"], color("red"))
        self.assert_escape_sequence(["32", "1"], color("green", bold=True))
        self.assert_escape_sequence(["0"], color("reset"))
        self.assert_escape_sequence(["45"], color("magenta", foreground=False))

    def test_mix_color_escape_sequence(self):
        self.assert_escape_sequence(["34", "1"],
                                    mix_color([color("blue"),
                                               color("none", bold=True)]))
        self.assert_escape_sequence(["34", "1", "4"],
                                    mix_color([color("blue"),
                                               color("none", bold=True)]) + \
                                        color("none", underline=True))

    def assert_escape_sequence(self, expected, color):
        self.assert_equal(expected, color.sequence)
        self.assert_match("\033\[(?:\\d+;)*\\d+m", color.escape_sequence)
        self.assert_equal(expected, color.escape_sequence[2:-1].split(";"))
