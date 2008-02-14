import re
import sys
import traceback
import os
import glob
import types
import time
import pprint

from pikzie.color import *
from pikzie.faults import *
from pikzie.assertions import Assertions
from pikzie.decorators import metadata

__all__ = ["TestSuite", "TestCase", "TestResult", "TestLoader"]

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

class AssertionFailure(Exception):
    def __init__(self, message, user_message=None):
        self.message = message
        self.user_message = user_message

    def __str__(self):
        result = self.message
        if self.user_message:
            result += self.user_message + "\n"
        return result

class PendingTestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class TestCaseRunner(object):
    def __init__(self, test_case, test_names):
        self.test_case = test_case
        self.test_names = test_names

    def tests(self):
        return map(lambda test_name: self.test_case(test_name), self.test_names)

    def run(self, result):
        if len(self.test_names) == 0:
            return

        result.on_start_test_case(self.test_case)
        for test in self.tests():
            test.run(result)
        result.on_finish_test_case(self.test_case)

class TestCaseTemplate(object):
    def setup(self):
        "Hook method for setting up the test fixture before exercising it."
        pass

    def teardown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

class TestCase(TestCaseTemplate, Assertions):
    """A class whose instances are single test cases.

    If the fixture may be used for many test cases, create as
    many test methods as are needed. When instantiating such a TestCase
    subclass, specify in the constructor arguments the name of the test method
    that the instance is to execute.

    Test authors should subclass TestCase for their own tests. Construction
    and deconstruction of the test's environment ('fixture') can be
    implemented by overriding the 'setup' and 'teardown' methods respectively.

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

    def get_metadata(self, name):
        metadata_container = self.metadata
        if metadata_container is None:
            return None
        return metadata_container.get(name)

    def metadata(self):
        test_method = self._test_method()
        metadata_container_key = metadata.container_key
        if not hasattr(test_method, metadata_container_key):
            return None
        return getattr(test_method, metadata_container_key)
    metadata = property(metadata)

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

    def short_name(self):
        return self.__method_name

    def __repr__(self):
        return "<%s method_name=%s description=%s>" % \
               (str(self.__class__), self.__method_name, self.__description)

    def run(self, result):
        try:
            self.__result = result
            result.on_start_test(self)

            success = False
            try:
                try:
                    self.setup()
                except PendingTestError:
                    self._pend_test(result)
                except KeyboardInterrupt:
                    result.interrupted()
                    return
                except:
                    self._add_error(result)
                    return

                try:
                    self._test_method()()
                    success = True
                except AssertionFailure:
                    self._add_failure(result)
                except PendingTestError:
                    self._pend_test(result)
                except KeyboardInterrupt:
                    result.interrupted()
                    return
                except:
                    self._add_error(result)
            finally:
                try:
                    self.teardown()
                except PendingTestError:
                    self._pend_test(result)
                except KeyboardInterrupt:
                    result.interrupted()
                except:
                    self._add_error(result)
                    success = False

            if success:
                result.add_success(self)
        finally:
            result.on_finish_test(self)
            self.__result = None

    def _test_method(self):
        return getattr(self, self.__method_name)

    def _pass_assertion(self):
        self.__result.pass_assertion(self)

    def _fail(self, message, user_message=None):
        raise AssertionFailure(message, user_message)

    def _pend(self, message):
        raise PendingTestError(message)

    def _notify(self, message):
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            frame = sys.exc_info()[2].tb_frame.f_back.f_back
        tracebacks = self._prepare_frame(frame, True)
        notification = Notification(self, message, tracebacks)
        self.__result.add_notification(self, notification)

    def _pformat_exception_class(self, exception_class):
        if issubclass(exception_class, Exception) or \
                issubclass(exception_class, types.ClassType):
            return str(exception_class)
        else:
            return pprint.pformat(exception_class)

    def _pformat_callable_object(self, callable_object):
        if hasattr(callable_object, "im_class"):
            cls = callable_object.im_class
            return "%s.%s.%s" % (cls.__module__,
                                 cls.__class__.__name__,
                                 callable_object.__name__)
        else:
            return "%s.%s" % (callable_object.__module__,
                              callable_object.__name__)

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
        result.add_failure(self, failure)

    def _add_error(self, result):
        exception_type, detail, traceback = sys.exc_info()
        tracebacks = self._prepare_traceback(traceback, False)
        error = Error(self, exception_type, detail, tracebacks)
        result.add_error(self, error)

    def _pend_test(self, result):
        exception_type, detail, traceback = sys.exc_info()
        tracebacks = self._prepare_traceback(traceback, True)
        pending = Pending(self, detail, tracebacks)
        result.pend_test(self, pending)

    def _prepare_traceback(self, tb, compute_length):
        while tb and self._is_relevant_frame_level(tb.tb_frame):
            tb = tb.tb_next
        length = None
        if compute_length:
            length = self._count_relevant_frame_levels(tb.tb_frame)
        stack_infos = traceback.extract_tb(tb, length)
        return self._create_traceback_objects(stack_infos)

    def _prepare_frame(self, frame, compute_length):
        while frame and self._is_relevant_frame_level(frame):
            frame = frame.f_back
        length = None
        if compute_length:
            length = self._count_relevant_frame_levels(frame)
        stack_infos = traceback.extract_stack(frame, length)
        return self._create_traceback_objects(stack_infos)

    def _create_traceback_objects(self, stack_infos):
        tracebacks = []
        for stack_info in stack_infos:
            filename, lineno, name, line = stack_info
            tracebacks.append(Traceback(filename, lineno, name, line))
        return tracebacks

    def _is_relevant_frame_level(self, frame):
        globals = frame.f_globals
        for cls in (TestCase,) + TestCase.__bases__:
            name = cls.__name__
            if globals.has_key(name) and globals[name] == cls:
                return True
        return False

    def _count_relevant_frame_levels(self, frame):
        length = 0
        while frame and not self._is_relevant_frame_level(frame):
            length += 1
            frame = frame.f_back
        return length


class TestLoader(object):
    default_pattern = "test/test_*.py"

    def __init__(self, pattern=None, test_names=None, test_case_names=None,
                 target_modules=None):
        self.pattern = pattern
        self.test_names = test_names
        self.test_case_names = test_case_names
        self.target_modules = target_modules or []

    def _get_test_names(self):
        return self._test_names
    def _set_test_names(self, names):
        self._test_names = self._prepare_target_names(names)
    test_names = property(_get_test_names, _set_test_names)

    def _get_test_case_names(self):
        return self._test_case_names
    def _set_test_case_names(self, names):
        self._test_case_names = self._prepare_target_names(names)
    test_case_names = property(_get_test_case_names, _set_test_case_names)

    def collect_test_cases(self, files=[]):
        test_cases = []
        for module in self._load_modules(files):
            for name in dir(module):
                object = getattr(module, name)
                def is_target_test_case_name():
                    if self.test_case_names is None: return True
                    def is_target_name(test_case_name):
                        if type(test_case_name) == str:
                            return test_case_name == name
                        else:
                            return test_case_name.search(name)
                    return len(filter(is_target_name, self.test_case_names)) > 0
                if (is_target_test_case_name() and
                    isinstance(object, (type, types.ClassType)) and
                    issubclass(object, TestCase)):
                    test_cases.append(object)
        return test_cases

    def create_test_suite(self, files=[]):
        tests = []
        for test_case in self.collect_test_cases(files):
            def _is_test_method(name):
                return self._is_test_method(test_case, name)
            target_tests = filter(_is_test_method, dir(test_case))
            if len(target_tests) > 0:
                tests.append(TestCaseRunner(test_case, target_tests))
        return TestSuite(tests)

    def _find_targets(self):
        targets = []
        for target in glob.glob(self.pattern or self.default_pattern):
            if os.path.isfile(target):
                targets.append(target)
        return targets

    def _load_modules(self, files=[]):
        modules = self.target_modules[:]
        targets = files
        if (len(files) == 0 and len(modules) == 0) or self.pattern is not None:
            targets += self._find_targets()
        for target in targets:
            target = os.path.splitext(target)[0]
            target = re.sub(re.escape(os.path.sep), ".", target)
            parts = target.split(".")
            module = None
            while len(parts) > 0 and module is None:
                name = ".".join(parts)
                __import__(name)
                module = sys.modules[name]
                parts.pop()
            if module is not None and module not in modules:
                modules.append(module)
        return modules

    def _is_test_method(self, test_case, name):
        if not name.startswith("test_"): return False
        if self.test_names is not None:
            def is_target_name(test_name):
                if type(test_name) == str:
                    return test_name == name
                else:
                    return test_name.search(name)
            if len(filter(is_target_name, self.test_names)) == 0:
                return False
        return callable(getattr(test_case, name))

    def _prepare_target_names(self, names):
        if names is None: return names
        if type(names) == str:
            names = [names]
        def prepare(name):
            if name.startswith("/") and name.endswith("/"):
                name = re.compile(name[1:-1])
            return name
        return map(prepare, names)

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
        self.elapsed = 0

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

    def n_pendings(self):
        return len(filter(lambda fault: isinstance(fault, Pending), self.faults))
    n_pendings = property(n_pendings)

    def n_notifications(self):
        return len(filter(lambda fault: isinstance(fault, Notification),
                          self.faults))
    n_notifications = property(n_notifications)

    def pass_assertion(self, test):
        self.n_assertions += 1
        self._notify("pass_assertion", test)

    def on_start_test(self, test):
        "Called when the given test is about to be run"
        self._start_at = time.time()
        self.n_tests += 1
        self._notify("start_test", test)

    def on_finish_test(self, test):
        "Called when the given test has been run"
        self._finish_at = time.time()
        self.elapsed += (self._finish_at - self._start_at)
        self._notify("finish_test", test)

    def on_start_test_case(self, test_case):
        "Called when the given test case is about to be run"
        self._notify("start_test_case", test_case)

    def on_finish_test_case(self, test_case):
        "Called when the given test case has been run"
        self._notify("finish_test_case", test_case)

    def add_error(self, test, error):
        """Called when an error has occurred."""
        self.faults.append(error)
        self._notify("error", error)

    def add_failure(self, test, failure):
        """Called when a failure has occurred."""
        self.faults.append(failure)
        self._notify("failure", failure)

    def add_notification(self, test, notification):
        """Called when a notification has occurred."""
        self.faults.append(notification)
        self._notify("notification", notification)

    def add_success(self, test):
        "Called when a test has completed successfully"
        self._notify("success", test)

    def pend_test(self, test, pending):
        """Called when a test is pended."""
        self.faults.append(pending)
        self._notify("pending", pending)

    def interrupt(self):
        "Indicates that the tests should be interrupted"
        self.interrupted = True

    def need_interrupt(self):
        return self.interrupted

    def succeeded(self):
        return len(filter(lambda fault: fault.critical, self.faults)) == 0
    succeeded = property(succeeded)

    def _notify(self, name, *args):
        for listner in self.listners:
            callback_name = "on_%s" % name
            if hasattr(listner, callback_name):
                getattr(listner, callback_name)(self, *args)

    def summary(self):
        return ("%d test(s), %d assertion(s), %d failure(s), %d error(s), " \
                    "%d pending(s), %d notification(s)") % \
            (self.n_tests, self.n_assertions, self.n_failures, self.n_errors,
             self.n_pendings, self.n_notifications)

    __str__ = summary
