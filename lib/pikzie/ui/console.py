import sys
import os
import math
import re

from optparse import OptionValueError

import pikzie.color
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
                         dest="use_color", nargs=1, type="string",
                         metavar="MODE", help=help)
    setup_color_option = classmethod(setup_color_option)

    def setup_color_scheme_option(cls, group):
        available_schemes = pikzie.color.SCHEMES.keys()
        help = "Use color scheme named SCHEME [%s]" % "|".join(available_schemes)
        group.add_option("--color-scheme", dest="color_scheme",
                         choices=available_schemes,
                         metavar="SCHEME", help=help)
    setup_color_scheme_option = classmethod(setup_color_scheme_option)

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
        cls.setup_color_scheme_option(group)
        cls.setup_verbose_option(group)
    setup_options = classmethod(setup_options)

    def __init__(self, output=sys.stdout, use_color=None, verbose_level=None,
                 color_scheme=None):
        if use_color is None:
            use_color = self._detect_color_availability()
        self.use_color = use_color
        if verbose_level is None:
            verbose_level = VERBOSE_LEVEL_NORMAL
        self.verbose_level = verbose_level
        self.output = output
        self.color_scheme = pikzie.color.SCHEMES[color_scheme or "default"]
        self.reset_color = pikzie.color.COLORS["reset"]

    def run(self, test, listeners=[]):
        "Run the given test case or test suite."
        result = TestResult()
        result.add_listeners([self] + listeners)
        test.run(result)
        if self.verbose_level == VERBOSE_LEVEL_NORMAL:
            self._writeln()
        self._print_faults(result)
        self._writeln("Finished in %.3f seconds" % result.elapsed)
        self._writeln()
        self._writeln(result.summary(), self._result_color(result))
        return result

    def on_start_test_case(self, result, test_case):
        description = self._generate_test_case_description(test_case)
        self._writeln("%s:%s" % (test_case.__name__, description),
                      self.color_scheme["test-case-name"],
                      level=VERBOSE_LEVEL_VERBOSE)

    def _generate_test_case_description(self, test_case):
        if not test_case.__doc__:
            return ""

        if re.search("\n", test_case.__doc__):
            lines = test_case.__doc__.rstrip().split("\n")
            min_indent = 1000
            for line in lines[1:]:
                if re.match(" *$", line):
                    continue
                min_indent = min([min_indent, re.match(" *", line).end()])
            lines = lines[0:1] + map(lambda line: line[min_indent:],
                                     lines[1:])
            lines = map(lambda line: " " + line, lines)
            return "\n%s" % "\n".join(lines)
        else:
            return " %s" % test_case.__doc__

    def on_start_test(self, result, test):
        self._n_notifications = 0

        if test.description():
            self._writeln(" %s" % test.description(),
                          level=VERBOSE_LEVEL_VERBOSE)

        test_name = test.short_name()
        indent = "  "
        result_mark = "."
        spaces = len(indent) + len(":") + len(result_mark)
        tab = "\t" * ((8 * 9 + spaces - len(test_name)) / 8)
        self._write("%s%s:%s" % (indent, test_name, tab),
                    level=VERBOSE_LEVEL_VERBOSE)

    def on_success(self, result, test):
        self._flood_notifications()
        self._write(".", self.color_scheme["success"])

    def _on_fault(self, result, fault):
        self._flood_notifications()
        self._write_fault(fault)

    on_failure = _on_fault
    on_error = _on_fault
    on_pending = _on_fault

    def on_notification(self, result, notification):
        self._pool_notification(notification)
        if self.verbose_level != VERBOSE_LEVEL_VERBOSE:
            self._write_fault(notification)
            return

        if self._n_notifications == 1:
            self._write_fault(notification)

    def on_finish_test(self, result, test):
        self._flood_notifications()
        self._writeln(level=VERBOSE_LEVEL_VERBOSE)

    def on_finish_test_case(self, result, test_case):
        self._writeln(level=VERBOSE_LEVEL_VERBOSE)

    def _pool_notification(self, notification):
        self._n_notifications += 1
        self._last_notification = notification

    def _flood_notifications(self):
        if self._n_notifications > 1:
            fault = self._last_notification
            color = self._fault_color(fault)
            if self._n_notifications > 3:
                message = "%d%s" % (self._n_notifications, fault.symbol)
            else:
                n_characters = self._n_notifications - 1
                message = fault.symbol * n_characters
            self._write(message, color, VERBOSE_LEVEL_VERBOSE)
        self._n_notifications = 0
        self._last_notification = None

    def _fault_color(self, fault):
        return self.color_scheme[fault.__class__.name]

    def _write(self, arg, color=None, level=VERBOSE_LEVEL_NORMAL):
        if self.verbose_level < level:
            return
        if self.use_color and color:
            arg = "%s%s%s" % (color.escape_sequence,
                              arg,
                              self.reset_color.escape_sequence)
        self.output.write(arg)
        self.output.flush()

    def _write_fault(self, fault, level=VERBOSE_LEVEL_NORMAL):
        self._write(fault.symbol, self._fault_color(fault), level)

    def _writeln(self, arg=None, color=None, level=VERBOSE_LEVEL_NORMAL):
        if arg:
            self._write(arg, color, level)
        self._write("\n", level=level)

    def _print_faults(self, result):
        size = len(result.faults)
        if size == 0:
            return
        self._writeln()
        index_format = "%%%dd) " % (math.floor(math.log10(size)) + 1)
        for i, fault in enumerate(result.faults):
            self._write(index_format % (i + 1))
            self._writeln(fault.title(), self._fault_color(fault))
            metadata = pikzie.faults.format_metadata(fault.test.metadata)
            if metadata:
                self._writeln(metadata, self._fault_color(fault))
            self._print_traceback(fault.traceback)
            detail = fault.detail()
            if detail:
                self._writeln(detail, self._fault_color(fault))
            self._writeln()

    def _print_traceback(self, traceback):
        if len(traceback) == 0:
            return
        for entry in traceback:
            self._write(entry.file_name, self._file_name_color())
            self._write(":")
            self._write("%d" % entry.line_number, self._line_number_color())
            if entry.content:
                self._write(": ")
                self._write(entry.content, self._content_color())
            self._writeln()

    def _result_color(self, result):
        if len(result.faults) == 0:
            return self.color_scheme["success"]
        else:
            return self._fault_color(sorted(result.faults, compare_fault)[0])

    def _file_name_color(self):
        return self.color_scheme["file-name"]

    def _line_number_color(self):
        return self.color_scheme["line-number"]

    def _content_color(self):
        return self.color_scheme["content"]

    def _detect_color_availability(self):
        term = os.getenv("TERM")
        if term and (term.endswith("term") or term == "screen"):
            return True
        emacs = os.getenv("EMACS")
        if emacs and (emacs == "t"):
            return True
        return False
