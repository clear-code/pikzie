import sys
import os
import math

from optparse import OptionValueError

from pikzie.color import COLORS
from pikzie.core import *
from pikzie.faults import *

class ConsoleTestRunner(object):
    def setup_options(cls, parser):
        available_values = "[yes|true|no|false|auto]"
        def store_use_color(option, opt, value, parser):
            if value == "yes" or value == "true":
                parser.values.use_color = True
            elif value == "no" or value == "false":
                parser.values.use_color = False
            elif value == "auto" or value is None:
                pass
            else:
                format = "should be one of %s: %s"
                raise OptionValueError(format % (available_values, value))

        help = "Output log with colors %s (default: auto)" % available_values
        parser.add_option("-c", "--color",
                          action="callback", callback=store_use_color,
                          dest="use_color", nargs=1, type="string", help=help)
    setup_options = classmethod(setup_options)

    def __init__(self, output=sys.stdout, use_color=None):
        if use_color is None:
            use_color = self._detect_color_availability()
        self.use_color = use_color
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
        pass

    def on_success(self, result, test):
        self._write(".", self._success_color())

    def _on_fault(self, result, fault):
        self._write(fault.single_character_display(), fault.color())

    on_failure = _on_fault
    on_error = _on_fault

    def _write(self, arg, color=None):
        if self.use_color and color:
            self.output.write("%s%s%s" % (color.escape_sequence,
                                          arg,
                                          COLORS["normal"].escape_sequence))
        else:
            self.output.write(arg)
        self.output.flush()

    def _writeln(self, arg=None, color=None):
        if arg:
            self._write(arg, color)
        self._write("\n")

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
