import sys
import os
import glob
import re
import types
import time
import math
import pprint

from pikzie.color import *
from pikzie.faults import *
from pikzie.test_case import TestCase

class TestSuite(object):
    """A test suite is a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    in the order in which they were added, aggregating the results. When
    subclassing, do not forget to call the base class constructor.
    """
    def __init__(self, tests=()):
        self._tests = []
        self.add_tests(tests)

    def __iter__(self):
        return iter(self._tests)

    def __len__(self):
        return sum(map(len, self._tests))

    def add_test(self, test):
        self._tests.append(test)

    def add_tests(self, tests):
        for test in tests:
            self.add_test(test)

    def run(self, result):
        for test in self._tests:
            test.run(result)
            if result.need_interrupt():
                break

class TestLoader(object):
    def __init__(self, pattern=None):
        if pattern is None:
            pattern = "**/test_*.py"
        self.pattern = pattern

    def find_targets(self):
        targets = []
        for target in glob.glob(self.pattern):
            if os.path.isfile(target):
                targets.append(target)
        return targets

    def load_modules(self):
        modules = []
        for target in self.find_targets():
            target = os.path.splitext(target)[0]
            target = re.sub(re.escape(os.path.sep), ".", target)
            parts = target.split(".")
            module = None
            while len(parts) > 0 and module is None:
                try:
                    name = ".".join(parts)
                    __import__(name)
                    module = sys.modules[name]
                except ImportError:
                    pass
                parts.pop()
            if module is not None:
                modules.append(module)
        return modules

    def collect_test_cases(self):
        test_cases = []
        for module in self.load_modules():
            for name in dir(module):
                object = getattr(module, name)
                if (isinstance(object, (type, types.ClassType)) and
                    issubclass(object, TestCase)):
                    test_cases.append(object)
        return test_cases

    def create_test_suite(self):
        tests = []
        for test_case in self.collect_test_cases():
            def is_test_method(name):
                return name.startswith("test_") and \
                    callable(getattr(test_case, name))
            tests.extend(map(test_case, filter(is_test_method, dir(test_case))))
        return TestSuite(tests)

class TestResult(object):
    """Holder for test result information.

    Test results are automatically managed by the TestCase and TestSuite
    classes, and do not need to be explicitly manipulated by writers of tests.

    Each instance holds the total number of tests run, and collections of
    failures and errors that occurred among those test runs. The collections
    contain tuples of (testcase, exceptioninfo), where exceptioninfo is the
    formatted traceback of the error that occurred.
    """
    def __init__(self):
        self.n_assertions = 0
        self.n_tests = 0
        self.faults = []
        self.listners = []
        self.interrupted = False

    def add_listner(self, listener):
        self.listners.append(listener)

    def n_faults(self):
        return len(self.faults)
    n_faults = property(n_faults)

    def n_failures(self):
        return len(filter(lambda fault: isinstance(fault, Failure), self.faults))
    n_failures = property(n_failures)

    def n_errors(self):
        return len(filter(lambda fault: isinstance(fault, Error), self.faults))
    n_errors = property(n_errors)

    def pass_assertion(self, test):
        self.n_assertions += 1
        self._notify("pass_assertion", test)

    def start_test(self, test):
        "Called when the given test is about to be run"
        self.n_tests += 1
        self._notify("start_test", test)

    def stop_test(self, test):
        "Called when the given test has been run"
        pass

    def add_error(self, test, error):
        """Called when an error has occurred."""
        self.faults.append(error)
        self._notify("error", error)

    def add_failure(self, test, failure):
        """Called when a failure has occurred."""
        self.faults.append(failure)
        self._notify("failure", failure)

    def add_success(self, test):
        "Called when a test has completed successfully"
        self._notify("success", test)

    def interrupt(self):
        "Indicates that the tests should be interrupted"
        self.interrupted = True

    def need_interrupt(self):
        return self.interrupted

    def succeeded(self):
        return len(self.faults) == 0

    def _notify(self, name, *args):
        for listner in self.listners:
            callback_name = "on_%s" % name
            if hasattr(listner, callback_name):
                getattr(listner, callback_name)(self, *args)

    def summary(self):
        return "%d test(s), %d assertion(s), %d failure(s), %d error(s)" % \
            (self.n_tests, self.n_assertions, self.n_failures, self.n_errors)

    __str__ = summary

class TextTestRunner(object):
    def __init__(self, output=sys.stdout, use_color=None):
        if use_color is None:
            term = os.getenv("TERM")
            use_color = term and term.endswith("term")
        self.use_color = use_color
        self.output = output

    def run(self, test):
        "Run the given test case or test suite."
        result = TestResult()
        result.add_listner(self)
        start = time.time()
        test.run(result)
        elapsed = time.time() - start
        self._writeln()
        self._writeln()
        self._print_errors(result)
        self._writeln("Finished in %.3f seconds" % elapsed)
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


class TestProgram(object):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """
    def __init__(self):
        pass

    def run(self, argv=sys.argv):
#         if not self._parse(argv):
#             return 2
        test = TestLoader().create_test_suite()
        runner = TextTestRunner()
        result = runner.run(test)
        if result.succeeded():
            return 0
        else:
            return 1
