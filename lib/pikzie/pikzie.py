import sys, os, glob, re, types, time, traceback, math, pprint, difflib
import unittest

TestSuite = unittest.TestSuite
FunctionTestCase = unittest.FunctionTestCase
main = unittest.main

version = "0.1"

__unittest = True

class Fault(Exception):
    def __init__(self, message, user_message=None):
        self.message = message
        self.user_message = user_message

    def __str__(self):
        result = self.message
        if self.user_message:
            result += self.user_message + "\n"
        return result

class TestCase(unittest.TestCase):
    failureException = Fault

    def __init__(self, *args):
        self._asserting = False
        unittest.TestCase.__init__(self, *args)

    def run(self, result=None):
        if result is None: result = self.defaultTestResult()
        self._result = result
        result.startTest(self)
        testMethod = getattr(self, self.__testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self.__exc_info())
                return

            ok = False
            try:
                testMethod()
                ok = True
            except self.failureException, e:
                result.addFailure(self, self.__exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self.__exc_info())

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self.__exc_info())
                ok = False
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)

    def fail(self, message):
        for _ in self._assertion():
            self._fail(message)

    def assert_none(self, expression, user_message=None):
        for _ in self._assertion():
            if expression is None:
                self._result.pass_assertion()
            else:
                message = "expected: <%r> is None" % expression
                self._fail(message, user_message)

    def assert_not_none(self, expression, user_message=None):
        for _ in self._assertion():
            if expression is not None:
                self._result.pass_assertion()
            else:
                self._fail("expected: not None", user_message)

    def assert_true(self, expression, user_message=None):
        for _ in self._assertion():
            if expression:
                self._result.pass_assertion()
            else:
                message = "expected: <%r> is a true value" % expression
                self._fail(message, user_message)

    def assert_false(self, expression, user_message=None):
        for _ in self._assertion():
            if expression:
                message = "expected: <%r> is a false value" % expression
                self._fail(message, user_message)
            else:
                self._result.pass_assertion()

    def assert_equal(self, expected, actual, user_message=None):
        for _ in self._assertion():
            if expected == actual:
                self._result.pass_assertion()
            else:
                expected = pprint.pformat(expected)
                actual = pprint.pformat(actual)
                diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
                message = "expected: <%s>\n but was: <%s>\ndiff:\n%s" % \
                    (expected, actual, "\n".join(diff))
                self._fail(message, user_message)

    def assert_not_equal(self, not_expected, actual, user_message=None):
        for _ in self._assertion():
            if not_expected != actual:
                self._result.pass_assertion()
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
        for _ in self._assertion():
            lower = expected - delta
            upper = expected + delta
            if lower <= actual <= upper:
                self._result.pass_assertion()
            else:
                expected = pprint.pformat(expected)
                actual = pprint.pformat(actual)
                delta = pprint.pformat(delta)
                range = pprint.pformat([lower, upper])
                message = "expected: <%s+-%s %s>\n but was: <%s>" % \
                    (expected, delta, range, actual)
                self._fail(message, user_message)

    def assert_match(self, pattern, target, user_message=None):
        for _ in self._assertion():
            if re.match(pattern, target):
                self._result.pass_assertion()
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
        for _ in self._assertion():
            if re.match(pattern, target) is None:
                self._result.pass_assertion()
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
        for _ in self._assertion():
            if re.search(pattern, target):
                self._result.pass_assertion()
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
        for _ in self._assertion():
            if re.search(pattern, target) is None:
                self._result.pass_assertion()
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
        for _ in self._assertion():
            if hasattr(object, name):
                self._result.pass_assertion()
            else:
                object = pprint.pformat(object)
                name = pprint.pformat(name)
                message = "expected: hasattr(%s, %s)" % (object, name)
                self._fail(message, user_message)

    def assert_callable(self, object, user_message=None):
        for _ in self._assertion():
            if callable(object):
                self._result.pass_assertion()
            else:
                object = pprint.pformat(object)
                message = "expected: callable(%s)" % (object)
                self._fail(message, user_message)

    def _fail(self, message, user_message=None):
        raise self.failureException(message, user_message)

    def _assertion(self):
        if self._asserting:
            yield self
        else:
            previous_asserting = self._asserting
            try:
                self._assertioning = True
                yield self
                self._asserting = previous_asserting
            except:
                self._asserting = previous_asserting
                raise

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

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self.__testMethodName)

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
                    issubclass(object, unittest.TestCase)):
                    test_cases.append(object)
        return test_cases

    def create_test_suite(self):
        tests = []
        for test_case in self.collect_test_cases():
            def is_test_method(name):
                return name.startswith("test_") and \
                    callable(getattr(test_case, name))
            tests.extend(map(test_case, filter(is_test_method, dir(test_case))))
        return unittest.TestSuite(tests)

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
        self.shouldStop = False
        self.listners = []

    def add_listner(self, listener):
        self.listners.append(listener)

    @property
    def n_faults(self):
        return len(self.faults)

    @property
    def n_failures(self):
        return len(filter(lambda fault: isinstance(fault, Failure), self.faults))

    @property
    def n_errors(self):
        return len(filter(lambda fault: isinstance(fault, Error), self.faults))

    def pass_assertion(self):
        self.n_assertions += 1
        self._notify("pass_assertion")

    def startTest(self, test):
        "Called when the given test is about to be run"
        self.n_tests += 1
        self._notify("start_test", test)

    def stopTest(self, test):
        "Called when the given test has been run"
        pass

    def addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        exception_type, detail, traceback = err
        tracebacks = self._prepare_traceback(traceback, False)
        error = Error(test, exception_type, detail, tracebacks)
        self.faults.append(error)
        self._notify("error", error)

    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        (exception_type, detail, traceback) = err
        tracebacks = self._prepare_traceback(traceback, True)
        failure = Failure(test, detail, tracebacks)
        self.faults.append(failure)
        self._notify("failure", failure)

    def addSuccess(self, test):
        "Called when a test has completed successfully"
        self._notify("success", test)

    def wasSuccessful(self):
        "Tells whether or not this result was a success"
        return self.n_faults == 0

    def stop(self):
        "Indicates that the tests should be aborted"
        self.shouldStop = True

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
        return tb.tb_frame.f_globals.has_key('__unittest')

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
        self.faults = []

    def run(self, test):
        "Run the given test case or test suite."
        result = TestResult()
        result.add_listner(self)
        start = time.time()
        test(result)
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
        self.faults.append(fault)

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

    def _succeeded(self):
        return len(self.faults) == 0

    def _print_errors(self, result):
        if self._succeeded():
            return
        size = len(self.faults)
        format = "%%%dd) %%s" % (math.floor(math.log10(size)) + 1)
        for i, fault in enumerate(self.faults):
            self._writeln(format % (i + 1, fault.long_display()),
                          fault.color())
            self._writeln()

    def _result_color(self, result):
        if self._succeeded():
            return self._success_color()
        else:
            def compare(x, y):
                return cmp(FAULT_RANK[type(x)], FAULT_RANK[type(y)])
            return sorted(self.faults, compare)[0].color()

    def _success_color(self):
        return COLORS["green"]


original_runTests = main.runTests
def runTests(self):
    self.test = TestLoader().create_test_suite()
    self.testRunner = TextTestRunner()
    original_runTests(self)

main.runTests = runTests
