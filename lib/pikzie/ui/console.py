import sys
import os
import math

from optparse import OptionValueError

from pikzie.color import COLORS
from pikzie.core import *
from pikzie.faults import *

VERBOSE_LEVEL_SILENT = 0
VERBOSE_LEVEL_NORMAL = 1
VERBOSE_LEVEL_VERBOSE = 2

class ConsoleTestRunner(object):
    def setup_color_option(cls, group):
        available_values = "[yes|true|no|false|auto]"
        def store_use_color(option, opt, value, parser):
            if value == "yes" or value == "true":
                parser.values.verbose_level = True
            elif value == "no" or value == "false":
                parser.values.use_color = False
            elif value == "auto" or value is None:
                pass
            else:
                format = "should be one of %s: %s"
                raise OptionValueError(format % (available_values, value))

        help = "Output log with colors %s (default: auto)" % available_values
        group.add_option("-c", "--color",
                         action="callback", callback=store_use_color,
                         dest="use_color", nargs=1, type="string", help=help)
    setup_color_option = classmethod(setup_color_option)

    def setup_verbose_option(cls, group):
        available_values = "[s|silent|n|normal|v|verbose]"
        def store_verbose_level(option, opt, value, parser):
            if value == "s" or value == "silent":
                parser.values.verbose_level = VERBOSE_LEVEL_SILENT
            elif value == "n" or value == "normal":
                parser.values.verbose_level = VERBOSE_LEVEL_NORMAL
            elif value == "v" or value == "verbose":
                parser.values.verbose_level = VERBOSE_LEVEL_VERBOSE
            else:
                format = "should be one of %s: %s"
                raise OptionValueError(format % (available_values, value))

        help = "Output level %s (default: normal)" % available_values
        group.add_option("-v", "--verbose",
                         action="callback", callback=store_verbose_level,
                         dest="verbose_level", nargs=1, type="string", help=help)
    setup_verbose_option = classmethod(setup_verbose_option)

    def setup_options(cls, parser):
        group = parser.add_option_group("Console UI", "Options for console UI")
        cls.setup_color_option(group)
        cls.setup_verbose_option(group)
    setup_options = classmethod(setup_options)

    def __init__(self, output=sys.stdout, use_color=None, verbose_level=None):
        if use_color is None:
            use_color = self._detect_color_availability()
        self.use_color = use_color
        if verbose_level is None:
            verbose_level = VERBOSE_LEVEL_NORMAL
        self.verbose_level = verbose_level
        self.output = output

    def run(self, test):
        "Run the given test case or test suite."
        result = TestResult()
        result.add_listner(self)
        test.run(result)
        self._writeln()
        self._writeln()
        self._print_errors(result)
        self._writeln("Finished in %.3f seconds" % result.elapsed)
        self._writeln()
        self._writeln(result.summary(), self._result_color(result))
        return result

    def on_start_test(self, result, test):
        test_name = str(test)
        indent = "  "
        result_mark = "."
        spaces = len(indent) + len(":") + len(result_mark)
        tab = "\t" * ((8 * 9 + spaces - len(test_name)) / 8)
        self._write("%s%s:%s" % (indent, test_name, tab),
                    level=VERBOSE_LEVEL_VERBOSE)

    def on_success(self, result, test):
        self._write(".", self._success_color())
        self._writeln(level=VERBOSE_LEVEL_VERBOSE)

    def _on_fault(self, result, fault):
        self._write(fault.single_character_display(), fault.color())

    on_failure = _on_fault
    on_error = _on_fault

    def _write(self, arg, color=None, level=VERBOSE_LEVEL_NORMAL):
        if self.verbose_level < level:
            return
        if self.use_color and color:
            self.output.write("%s%s%s" % (color.escape_sequence,
                                          arg,
                                          COLORS["normal"].escape_sequence))
        else:
            self.output.write(arg)
        self.output.flush()

    def _writeln(self, arg=None, color=None, level=VERBOSE_LEVEL_NORMAL):
        if arg:
            self._write(arg, color, level)
        self._write("\n", level=level)

    def _print_errors(self, result):
        if result.succeeded():
            return
        size = len(result.faults)
        format = "%%%dd) %%s" % (math.floor(math.log10(size)) + 1)
        for i, fault in enumerate(result.faults):
            self._writeln(format % (i + 1, fault.long_display()),
                          fault.color())
            self._writeln()

    def _result_color(self, result):
        if result.succeeded():
            return self._success_color()
        else:
            return sorted(result.faults, compare_fault)[0].color()

    def _success_color(self):
        return COLORS["green"]

    def _detect_color_availability(self):
        term = os.getenv("TERM")
        return term and term.endswith("term")
