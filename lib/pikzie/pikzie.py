import sys
import os
import glob
import re
import types
import time
import traceback
import math
import pprint
import difflib

version = "0.1"

__pikzie = True


class Fault(Exception):
    def __init__(self, message, user_message=None):
        self.message = message
        self.user_message = user_message

    def __str__(self):
        result = self.message
        if self.user_message:
            result += self.user_message + "\n"
        return result

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

class TestCase(object):
    """A class whose instances are single test cases.

    By default, the test code itself should be placed in a method named
    'runTest'.

    If the fixture may be used for many test cases, create as
    many test methods as are needed. When instantiating such a TestCase
    subclass, specify in the constructor arguments the name of the test method
    that the instance is to execute.

    Test authors should subclass TestCase for their own tests. Construction
    and deconstruction of the test's environment ('fixture') can be
    implemented by overriding the 'setUp' and 'tearDown' methods respectively.

    If it is necessary to override the __init__ method, the base class
    __init__ method must always be called. It is important that subclasses
    should not change the signature of their __init__ method, since instances
    of the classes are instantiated automatically by parts of the framework
    in order to be run.
    """

    def __init__(self, method_name):
        self.__method_name = method_name
        self.__description = getattr(self, method_name).__doc__

    def __len__(self):
        return 1

    def description(self):
        """Returns a one-line description of the test, or None if no
        description has been provided.

        The default implementation of this method returns the first line of
        the specified test method's docstring.
        """
        description = self.__description
        if description:
            return description.split("\n")[0].strip()
        else:
            return None

    def id(self):
        return "%s.%s.%s" % (self.__class__.__module__,
                             self.__class__.__name__,
                             self.__method_name)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self.__method_name)

    def __repr__(self):
        return "<%s method_name=%s description=%s>" % \
               (str(self.__class__), self.__method_name, self.__description)

    def run(self, result):
        try:
            self.__result = result
            result.start_test(self)

            success = False
            try:
                try:
                    self.setup()
                except KeyboardInterrupt:
                    result.interrupted()
                    return
                except:
                    result.add_error(self, sys.exc_info())
                    return

                try:
                    getattr(self, self.__method_name)()
                    success = True
                except Fault:
                    result.add_failure(self, sys.exc_info())
                except KeyboardInterrupt:
                    result.interrupted()
                    return
                except:
                    result.add_error(self, sys.exc_info())
            finally:
                try:
                    self.teardown()
                except KeyboardInterrupt:
                    result.interrupted()
                except:
                    result.add_error(self, sys.exc_info())
                    success = False

            if success:
                result.add_success(self)
        finally:
            result.stop_test(self)
            self.__result = None

    def setup(self):
        "Hook method for setting up the test fixture before exercising it."
        pass

    def teardown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

    def fail(self, message):
        self._fail(message)

    def assert_none(self, expression, user_message=None):
        if expression is None:
            self._pass_assertion()
        else:
            message = "expected: <%r> is None" % expression
            self._fail(message, user_message)

    def assert_not_none(self, expression, user_message=None):
        if expression is not None:
            self._pass_assertion()
        else:
            self._fail("expected: not None", user_message)

    def assert_true(self, expression, user_message=None):
        if expression:
            self._pass_assertion()
        else:
            message = "expected: <%r> is a true value" % expression
            self._fail(message, user_message)

    def assert_false(self, expression, user_message=None):
        if expression:
            message = "expected: <%r> is a false value" % expression
            self._fail(message, user_message)
        else:
            self._pass_assertion()

    def assert_equal(self, expected, actual, user_message=None):
        if expected == actual:
            self._pass_assertion()
        else:
            expected = pprint.pformat(expected)
            actual = pprint.pformat(actual)
            diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
            message = "expected: <%s>\n but was: <%s>\ndiff:\n%s" % \
                (expected, actual, "\n".join(diff))
            self._fail(message, user_message)

    def assert_not_equal(self, not_expected, actual, user_message=None):
        if not_expected != actual:
            self._pass_assertion()
        else:
            not_expected = pprint.pformat(not_expected)
            actual = pprint.pformat(actual)
            message = "not expected: <%s>\n     but was: <%s>" % \
                (not_expected, actual)
            if not_expected != actual:
                diff = difflib.ndiff(not_expected.splitlines(),
                                     actual.splitlines())
                message = "%s\ndiff:\n%s" % (message, "\n".join(diff))
            self._fail(message, user_message)

    def assert_in_delta(self, expected, actual, delta, user_message=None):
        lower = expected - delta
        upper = expected + delta
        if lower <= actual <= upper:
            self._pass_assertion()
        else:
            expected = pprint.pformat(expected)
            actual = pprint.pformat(actual)
            delta = pprint.pformat(delta)
            range = pprint.pformat([lower, upper])
            message = "expected: <%s+-%s %s>\n but was: <%s>" % \
                (expected, delta, range, actual)
            self._fail(message, user_message)

    def assert_match(self, pattern, target, user_message=None):
        if re.match(pattern, target):
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.match(%s, %s) is not None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            message = format % (pattern_repr, target, pattern, target)
            self._fail(message, user_message)

    def assert_not_match(self, pattern, target, user_message=None):
        if re.match(pattern, target) is None:
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.match(%s, %s) is None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            message = format % (pattern_repr, target, pattern, target)
            self._fail(message, user_message)

    def assert_search(self, pattern, target, user_message=None):
        if re.search(pattern, target):
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.search(%s, %s) is not None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            message = format % (pattern_repr, target, pattern, target)
            self._fail(message, user_message)

    def assert_not_found(self, pattern, target, user_message=None):
        if re.search(pattern, target) is None:
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.search(%s, %s) is None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            message = format % (pattern_repr, target, pattern, target)
            self._fail(message, user_message)

    def assert_hasattr(self, object, name, user_message=None):
        if hasattr(object, name):
            self._pass_assertion()
        else:
            object = pprint.pformat(object)
            name = pprint.pformat(name)
            message = "expected: hasattr(%s, %s)" % (object, name)
            self._fail(message, user_message)

    def assert_callable(self, object, user_message=None):
        if callable(object):
            self._pass_assertion()
        else:
            object = pprint.pformat(object)
            message = "expected: callable(%s)" % (object)
            self._fail(message, user_message)

    def assert_call_raise(self, exception, callable_object, *args, **kw_args):
        try:
            callable_object(*args, **kw_args)
        except exception:
            self._pass_assertion()
        except:
            actual = sys.exc_info()
            actual_exception_class, actual_exception_value = actual[:2]
            message = \
                "expected: <%s> is raised\n" \
                " but was: <%s>(%s)" % \
                (self._pformat_exception_class(exception),
                 self._pformat_exception_class(actual_exception_class),
                 str(actual_exception_value))
            self._fail(message)
        else:
            message = \
                "expected: <%s> is raised\n" \
                " but was: nothing raised" % \
                self._pformat_exception_class(exception)
            self._fail(message)

    def _pass_assertion(self):
        self.__result.pass_assertion(self)

    def _fail(self, message, user_message=None):
        raise Fault(message, user_message)

    def _pformat_exception_class(self, exception_class):
        if issubclass(exception_class, Exception) or \
                issubclass(exception_class, types.ClassType):
            return str(exception_class)
        else:
            return pprint.pformat(exception_class)

    def _pformat_re(self, pattern):
        re_flags = self._re_flags(pattern)
        if hasattr(pattern, "pattern"):
            pattern = pattern.pattern
        pattern = pprint.pformat(pattern)
        return "/%s/%s" % (pattern[1:-1], re_flags)

    def _pformat_re_repr(self, pattern):
        re_flags_repr = self._re_flags_repr(pattern)
        if hasattr(pattern, "pattern"):
            pattern = pattern.pattern
        pattern = pprint.pformat(pattern)
        if re_flags_repr:
            return "re.compile(%s, %s)" % (pattern, re_flags_repr)
        else:
            return pattern

    _re_class = type(re.compile(""))
    def _re_flags(self, pattern):
        result = ""
        if isinstance(pattern, self._re_class):
            if pattern.flags & re.IGNORECASE: result += "i"
            if pattern.flags & re.LOCALE: result += "l"
            if pattern.flags & re.MULTILINE: result += "m"
            if pattern.flags & re.DOTALL: result += "d"
            if pattern.flags & re.UNICODE: result += "u"
            if pattern.flags & re.VERBOSE: result += "x"
        return result

    def _re_flags_repr(self, pattern):
        flags = []
        if isinstance(pattern, self._re_class):
            if pattern.flags & re.IGNORECASE: flags.append("re.IGNORECASE")
            if pattern.flags & re.LOCALE: flags.append("re.LOCALE")
            if pattern.flags & re.MULTILINE: flags.append("re.MULTILINE")
            if pattern.flags & re.DOTALL: flags.append("re.DOTALL")
            if pattern.flags & re.UNICODE: flags.append("re.UNICODE")
            if pattern.flags & re.VERBOSE: flags.append("re.VERBOSE")
        if len(flags) == 0:
            return None
        else:
            return " | ".join(flags)

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

class Traceback(object):
    def __init__(self, filename, lineno, name, line):
        self.filename = filename
        self.lineno = lineno
        self.name = name
        self.line = line

    def __str__(self):
        result = '%s:%d: %s()' % (self.filename, self.lineno, self.name)
        if self.line:
            result = "%s: %s" % (result, self.line)
        return result

class Color(object):
    def __init__(self, name, escape_sequence):
        self.name = name
        self.escape_sequence = escape_sequence

COLORS = {
    "red": Color("red", "\033[01;31m"),
    "red-back": Color("red-back", "\033[41m"),
    "green": Color("green", "\033[01;32m"),
    "green-back": Color("green-back", "\033[01;42m"),
    "yellow": Color("yellow", "\033[01;33m"),
    "blue": Color("blue", "\033[01;34m"),
    "purple": Color("purple", "\033[01;35m"),
    "cyan": Color("cyan", "\033[01;36m"),
    "white": Color("white", "\033[01;37m"),
    "normal": Color("normal", "\033[00m"),
    }

class Failure(object):
    def __init__(self, test, detail, tracebacks):
        self.test = test
        self.detail = detail
        self.tracebacks = tracebacks

    def single_character_display(self):
        return "F"

    def color(self):
        return COLORS["red"]

    def long_display(self):
        if len(self.tracebacks) == 0:
            return "Failure: %s\n%s" % (self.test, self.detail)
        else:
            return "Failure: %s: %s\n%s\n%s" % \
                (self.test, self.tracebacks[0].line,
                 self.detail, "\n".join(map(str, self.tracebacks)))

class Error(object):
    def __init__(self, test, exception_type, detail, tracebacks):
        self.test = test
        self.exception_type = exception_type
        self.detail = detail
        self.tracebacks = tracebacks

    def single_character_display(self):
        return "E"

    def color(self):
        return COLORS["purple"]

    def long_display(self):
        return "Error: %s\n%s: %s\n%s" % \
            (self.test, self.exception_type,
             self.detail, "\n".join(map(str, self.tracebacks)))

FAULT_RANK = {
    Failure: 0,
    Error: 1,
    }

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

    def add_error(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        exception_type, detail, traceback = err
        tracebacks = self._prepare_traceback(traceback, False)
        error = Error(test, exception_type, detail, tracebacks)
        self.faults.append(error)
        self._notify("error", error)

    def add_failure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        (exception_type, detail, traceback) = err
        tracebacks = self._prepare_traceback(traceback, True)
        failure = Failure(test, detail, tracebacks)
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

    def _prepare_traceback(self, tb, compute_length):
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next
        length = None
        if compute_length:
            length = self._count_relevant_tb_levels(tb)
        tracebacks = []
        for tb in traceback.extract_tb(tb, length):
            filename, lineno, name, line = tb
            tracebacks.append(Traceback(filename, lineno, name, line))
        return tracebacks

    def _is_relevant_tb_level(self, tb):
        return tb.tb_frame.f_globals.has_key('__pikzie')

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length

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
            def compare(x, y):
                return cmp(FAULT_RANK[type(x)], FAULT_RANK[type(y)])
            return sorted(result.faults, compare)[0].color()

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
