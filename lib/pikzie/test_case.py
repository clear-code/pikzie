import pprint
import re
import sys
import traceback
from faults import *
from assertions import Assertions

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

class TestCaseTemplate(object):
    def setup(self):
        "Hook method for setting up the test fixture before exercising it."
        pass

    def teardown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

class TestCase(TestCaseTemplate, Assertions):
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
                    self._add_error(result)
                    return

                try:
                    getattr(self, self.__method_name)()
                    success = True
                except Fault:
                    self._add_failure(result)
                except KeyboardInterrupt:
                    result.interrupted()
                    return
                except:
                    self._add_error(result)
            finally:
                try:
                    self.teardown()
                except KeyboardInterrupt:
                    result.interrupted()
                except:
                    self._add_error(result)
                    success = False

            if success:
                result.add_success(self)
        finally:
            result.stop_test(self)
            self.__result = None

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

    def _add_failure(self, result):
        exception_type, detail, traceback = sys.exc_info()
        tracebacks = self._prepare_traceback(traceback, True)
        failure = Failure(self, detail, tracebacks)
        result.add_error(self, failure)

    def _add_error(self, result):
        exception_type, detail, traceback = sys.exc_info()
        tracebacks = self._prepare_traceback(traceback, False)
        error = Error(self, exception_type, detail, tracebacks)
        result.add_error(self, error)

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
        globals = tb.tb_frame.f_globals
        for cls in (TestCase,) + TestCase.__bases__:
            name = cls.__name__
            if globals.has_key(name) and globals[name] == cls:
                return True
        return False

    def _count_relevant_tb_levels(self, tb):
        length = 0
        while tb and not self._is_relevant_tb_level(tb):
            length += 1
            tb = tb.tb_next
        return length
