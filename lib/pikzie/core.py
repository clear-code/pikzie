# Copyright (C) 2009-2011  Kouhei Sutou <kou@clear-code.com>
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

import re
import sys
import traceback
import os
import errno
import fnmatch
import types
import time
import tempfile

from pikzie.color import *
from pikzie.results import *
from pikzie.assertions import Assertions
from pikzie.decorators import metadata
from pikzie.priority import PriorityChecker

__all__ = ["TestSuite", "TestCase", "TestRunnerContext", "TestLoader"]

class TestSuite(object):
    """
    A test suite is a composite test consisting of a number of TestCases.

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

    def run(self, context):
        context.on_start_test_suite(self)
        for test in self._tests:
            test.run(context)
            if context.need_interrupt():
                break
        context.on_finish_test_suite(self)

class TracebackEntry(object):
    def __init__(self, file_name, line_number, name, content):
        self.file_name = file_name
        self.line_number = line_number
        self.name = name
        self.content = content

    def __str__(self):
        result = '%s:%d: %s()' % (self.file_name, self.line_number, self.name)
        if self.content:
            result = "%s: %s" % (result, self.content)
        return result

class AssertionFailure(Exception):
    def __init__(self, message, user_message=None, expected=None, actual=None):
        self.message = message
        self.user_message = user_message
        self.expected = expected
        self.actual = actual

    def __str__(self):
        result = self.message
        if self.user_message:
            result = "%s\n%s" % (str(self.user_message).rstrip(), result)
        return result

class PendingTestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class OmissionTestError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class TestCaseRunner(object):
    def __init__(self, test_case, tests, priority_mode=True):
        self.test_case = test_case
        self._tests = tests
        self.priority_mode = priority_mode

    def tests(self):
        tests = self._tests
        if self.priority_mode:
            tests = [test for test in tests if test.need_to_run()]
        return tests

    def run(self, context):
        tests = self.tests()
        if len(tests) == 0:
            return

        context.on_start_test_case(self.test_case)
        for test in tests:
            test.run(context)
            if context.need_interrupt():
                break
        context.on_finish_test_case(self.test_case)

class TestCaseTemplate(object):
    def setup(self):
        "Hook method for setting up the test fixture before exercising it."
        pass

    def teardown(self):
        "Hook method for deconstructing the test fixture after testing it."
        pass

class TestCase(TestCaseTemplate, Assertions):
    """
    A class whose instances are single test cases.

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

    def _collect_test(cls, target, base_n_args):
        def is_function(object):
            return ((hasattr(object, "__code__") and
                     hasattr(object.__code__, "co_argcount")) or
                    (hasattr(object, "func_code") and
                     hasattr(object.func_code, "co_argcount")))
        def test_data(object):
            if not hasattr(object, metadata.container_key):
                return None
            return getattr(object, metadata.container_key).get("data")

        tests = []
        for name in dir(target):
            object = getattr(target, name)
            if not is_function(object):
                continue
            if hasattr(object, "__code__"):
                code = object.__code__
            else:
                code = object.func_code
            n_args = code.co_argcount
            data = test_data(object)
            if data is None:
                if n_args == base_n_args:
                    tests.append(cls(name))
            else:
                if not n_args == base_n_args + 1:
                    continue
                for datum in data:
                    tests.append(cls(name, datum["label"], datum["value"]))
        return tests
    _collect_test = classmethod(_collect_test)

    def collect_test(cls):
        return cls._collect_test(cls, 1)
    collect_test = classmethod(collect_test)

    def __init__(self, method_name, data_label=None, data=None):
        self.__method_name = method_name
        self.__description = self._test_method().__doc__
        self.__data_label = data_label
        self.__data = data

    def _data(self):
        return self.__data

    def _data_label(self):
        return self.__data_label

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
        """
        Returns a one-line description of the test, or None if no
        description has been provided.

        The default implementation of this method returns the first line of
        the specified test method's docstring.
        """
        description = self.__description
        if description:
            return description.split("\n")[0].strip()
        else:
            return None

    def _test_case_name(self):
        return "%s.%s" % (self.__class__.__module__,
                          self.__class__.__name__)

    def id(self):
        id = "%s.%s" % (self._test_case_name(), self._method_name())
        if self.__data_label:
            id += " (%s)" % self.__data_label
        return id

    def __str__(self):
        string = "%s.%s" % (self.__class__.__name__, self._method_name())
        if self.__data_label:
            string += " (%s)" % self.__data_label
        return string

    def short_name(self):
        name = self.__method_name
        if self.__data_label:
            name += " (%s)" % self.__data_label
        return name

    def __repr__(self):
        return "<%s method_name=%s description=%s data_label=%s data=%s>" % \
            (str(self.__class__), self.__method_name, self.__description,
             self.__data_label, str(self.__data))

    def need_to_run(self):
        return not self._is_previous_test_success() or \
            self._need_to_run_according_to_priority()

    def run(self, context):
        success = False
        try:
            self._started(context)

            try:
                try:
                    self._run_setup(context)
                except PendingTestError:
                    self._pend_test(context)
                except OmissionTestError:
                    self._omit_test(context)
                except KeyboardInterrupt:
                    context.interrupt()
                    return
                except:
                    self._add_error(context)
                    return

                try:
                    self._run_test(context)
                    success = True
                except AssertionFailure:
                    self._add_failure(context)
                except PendingTestError:
                    self._pend_test(context)
                except OmissionTestError:
                    self._omit_test(context)
                except KeyboardInterrupt:
                    context.interrupt()
                    return
                except:
                    self._add_error(context)
            finally:
                try:
                    self._run_teardown(context)
                except PendingTestError:
                    self._pend_test(context)
                except OmissionTestError:
                    self._omit_test(context)
                except KeyboardInterrupt:
                    context.interrupt()
                except:
                    self._add_error(context)
                    success = False

        finally:
            self._finished(success, context)

    def _run_setup(self, context):
        self.setup()

    def _run_test(self, context):
        test_method = self._test_method()
        if self.__data_label:
            test_method(self.__data)
        else:
            test_method()

    def _run_teardown(self, context):
        self.teardown()

    def _method_name(self):
        return self.__method_name

    def _test_method(self):
        return getattr(self, self._method_name())

    def _pass_assertion(self):
        self.__context.pass_assertion(self)

    def _fail(self, message, user_message=None, expected=None, actual=None):
        raise AssertionFailure(message, user_message, expected, actual)

    def _pend(self, message):
        raise PendingTestError(message)

    def _omit(self, message):
        raise OmissionTestError(message)

    def _notify(self, message):
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            frame = sys.exc_info()[2].tb_frame.f_back.f_back
        traceback = self._prepare_frame(frame, True)
        notification = Notification(self, message, traceback)
        self.__context.add_notification(self, notification)

    def _started(self, context):
        self.__context = context
        context.on_start_test(self)
        if os.path.exists(self._passed_file()):
            os.remove(self._passed_file())

    def _finished(self, success, context):
        if success:
            self._add_success(context)
        context.on_finish_test(self)
        self.__context = None

    def _add_success(self, context):
        open(self._passed_file(), "w").close()
        context.add_success(self)

    def _add_failure(self, context):
        exception_type, assertion_failure, traceback = sys.exc_info()
        traceback = self._prepare_traceback(traceback, True)
        failure = Failure(self, str(assertion_failure), traceback,
                          assertion_failure.expected,
                          assertion_failure.actual)
        context.add_failure(self, failure)

    def _add_error(self, context):
        exception_type, message, traceback = sys.exc_info()
        traceback = self._prepare_traceback(traceback, False)
        error = Error(self, exception_type, message, traceback)
        context.add_error(self, error)

    def _pend_test(self, context):
        exception_type, message, traceback = sys.exc_info()
        traceback = self._prepare_traceback(traceback, True)
        pending = Pending(self, message, traceback)
        context.pend_test(self, pending)

    def _omit_test(self, context):
        exception_type, message, traceback = sys.exc_info()
        traceback = self._prepare_traceback(traceback, True)
        omission = Omission(self, message, traceback)
        context.omit_test(self, omission)

    def _prepare_traceback(self, tb, compute_length):
        while tb and self._is_relevant_frame_level(tb.tb_frame):
            tb = tb.tb_next
        length = None
        if tb and compute_length:
            length = self._count_relevant_frame_levels(tb.tb_frame)
        stack_infos = traceback.extract_tb(tb, length)
        return self._create_traceback_entries(stack_infos)

    def _prepare_frame(self, frame, compute_length):
        while frame and self._is_relevant_frame_level(frame):
            frame = frame.f_back
        length = None
        if compute_length:
            length = self._count_relevant_frame_levels(frame)
        stack_infos = traceback.extract_stack(frame, length)
        return self._create_traceback_entries(stack_infos)

    def _create_traceback_entries(self, stack_infos):
        entries = []
        for stack_info in stack_infos:
            filename, lineno, name, line = stack_info
            entries.append(TracebackEntry(filename, lineno, name, line))
        return entries

    def _is_relevant_frame_level(self, frame):
        globals = frame.f_globals
        for cls in (TestCase,) + TestCase.__bases__:
            name = cls.__name__
            if name in globals and globals[name] == cls:
                return True
        return False

    def _count_relevant_frame_levels(self, frame):
        length = 0
        while frame and not self._is_relevant_frame_level(frame):
            length += 1
            frame = frame.f_back
        return length

    def _is_previous_test_success(self):
        return os.path.exists(self._passed_file())

    def _passed_file(self):
        return os.path.join(self._result_dir(), "passed")

    def _result_dir(self):
        components = [".test-result", self._test_case_name(), self.short_name()]
        parent_directories = [os.path.dirname(sys.argv[0]),
                              os.getcwd(),
                              os.path.join(os.path.dirname(__file__), "..")]
        if hasattr(os, "getuid"):
            parent_directories.append([os.path.join(tempfile.gettempdir(),
                                                    str(os.getuid()))])
        else:
            parent_directories.append([os.path.join(tempfile.gettempdir(),
                                                    str(os.getpid()))])
        for parent_directory in parent_directories:
            dir = os.path.abspath(os.path.join(parent_directory, *components))
            if os.path.isdir(dir):
                return dir
            try:
                os.makedirs(dir)
                return dir
            except OSError:
                pass

        raise OSError(errno.EACCES, "Permission denied",
                      ", ".join(parent_directories))

    default_priority = "normal"
    def _need_to_run_according_to_priority(self):
        priority = self.get_metadata("priority")
        if priority is None:
            priority = self.default_priority
        if hasattr(PriorityChecker, priority):
            return getattr(PriorityChecker, priority)()
        else:
            return True

class TestLoader(object):
    default_base_dir = os.path.dirname(sys.argv[0])
    default_pattern = "test[_-]*.py"
    default_ignore_dirs = [".svn", "CVS", ".git", ".test-result"]

    def __init__(self, base_dir=None, pattern=None, ignore_dirs=None,
                 test_names=None, test_case_names=None,
                 target_modules=None, priority_mode=True):
        self.base_dir = base_dir
        self.pattern = pattern
        self.ignore_dirs = ignore_dirs
        self.test_names = test_names
        self.test_case_names = test_case_names
        self.target_modules = target_modules or []
        self.priority_mode = priority_mode

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

    test_case_collectors = []

    _class_types = [type]
    if "ClassType" in types.__dict__:
        _class_types.append(types.ClassType)
    _class_types = tuple(_class_types)
    def _collect_test_case_from_module(self, module):
        test_cases = []
        for name in dir(module):
            object = getattr(module, name)
            if (isinstance(object, self._class_types) and
                issubclass(object, TestCase)):
                test_cases.append(object)
        return test_cases
    test_case_collectors.append(_collect_test_case_from_module)

    def collect_test_cases(self, files=[]):
        test_cases = []
        for module in self._load_modules(files):
            for test_case_collector in self.test_case_collectors:
                test_cases.extend(test_case_collector(self, module))

        def is_target_test_case_name(test_case):
            name = test_case.__name__
            if self.test_case_names is None:
                return True
            def is_target_name(test_case_name):
                if type(test_case_name) == str:
                    return test_case_name == name
                else:
                    return test_case_name.search(name)
            return len(list(filter(is_target_name, self.test_case_names))) > 0

        return list(filter(is_target_test_case_name, test_cases))

    def create_test_suite(self, files=[]):
        tests = []
        for test_case in self.collect_test_cases(files):
            def _is_target_test(test):
                return self._is_target_test(test)
            target_tests = filter(_is_target_test, test_case.collect_test())
            target_tests = list(target_tests)
            if len(target_tests) > 0:
                tests.append(TestCaseRunner(test_case, target_tests,
                                            self.priority_mode))
        return TestSuite(tests)

    def _find_targets(self):
        targets = []
        base_dir = os.path.abspath(self.base_dir or self.default_base_dir)
        pattern = self.pattern or self.default_pattern
        ignore_dirs = (self.ignore_dirs or []) + self.default_ignore_dirs
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if fnmatch.fnmatch(file, pattern):
                    targets.append(re.sub("^\./", "", os.path.join(root, file)))
            for ignore_dir in ignore_dirs:
                if ignore_dir in dirs:
                    dirs.remove(ignore_dir)
        return (base_dir,
                map(lambda path: re.sub("^%s\/" % re.escape(base_dir), "", path),
                    targets))

    def _need_load_files(self, files, modules):
        if self.pattern is not None:
            return True
        if len(files) == 0 and len(modules) == 0:
            return True
        return False

    def _load_modules(self, files=[]):
        modules = self.target_modules[:]
        targets = files[:]
        base_dir = None
        if self._need_load_files(files, modules):
            base_dir, _targets = self._find_targets()
            targets += _targets
        if base_dir:
            base_dir = os.path.abspath(base_dir)
            sys.path.insert(0, base_dir)
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
        if base_dir:
            sys.path.remove(base_dir)
        return modules

    def _is_target_test(self, test):
        name = test.short_name()
        if not name.startswith("test_"):
            return False
        if self.test_names is not None:
            def is_target_name(test_name):
                if type(test_name) == str:
                    return test_name == name
                else:
                    return test_name.search(name)
            if len(list(filter(is_target_name, self.test_names))) == 0:
                return False
        return True

    def _prepare_target_names(self, names):
        if names is None: return names
        if type(names) == str:
            names = [names]
        re_re = re.compile("/(.*)/([ilmsux]*)")
        def prepare(name):
            match = re_re.search(name)
            if match:
                flags = 0
                for flag_string in match.groups()[1]:
                    flags |= getattr(re, flag_string.upper())
                name = re.compile(match.groups()[0], flags)
            return name
        return [prepare(name) for name in names]

class TestRunnerContext(object):
    """
    Context for running test.

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
        self.results = []
        self.listeners = []
        self.interrupted = False
        self.elapsed = 0

    def add_listener(self, listener):
        self.listeners.append(listener)

    def add_listeners(self, listeners):
        self.listeners.extend(listeners)

    def faults(self):
        return list(filter(lambda result: result.fault, self.results))
    faults = property(faults)

    def n_faults(self):
        return len(self.faults)
    n_faults = property(n_faults)

    def n_failures(self):
        return len(list(filter(lambda result: isinstance(result, Failure),
                               self.results)))
    n_failures = property(n_failures)

    def n_errors(self):
        return len(list(filter(lambda result: isinstance(result, Error),
                               self.results)))
    n_errors = property(n_errors)

    def n_pendings(self):
        return len(list(filter(lambda result: isinstance(result, Pending),
                               self.results)))
    n_pendings = property(n_pendings)

    def n_omissions(self):
        return len(list(filter(lambda result: isinstance(result, Omission),
                               self.results)))
    n_omissions = property(n_omissions)

    def n_notifications(self):
        return len(list(filter(lambda result: isinstance(result, Notification),
                               self.results)))
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

    def on_start_test_suite(self, test_suite):
        "Called when the given test suite is about to be run"
        self._notify("start_test_suite", test_suite)

    def on_finish_test_suite(self, test_suite):
        "Called when the given test suite has been run"
        self._notify("finish_test_suite", test_suite)

    def add_error(self, test, error):
        """Called when an error has occurred."""
        error.elapsed = time.time() - self._start_at
        self.results.append(error)
        self._notify("error", error)

    def add_failure(self, test, failure):
        """Called when a failure has occurred."""
        failure.elapsed = time.time() - self._start_at
        self.results.append(failure)
        self._notify("failure", failure)

    def add_notification(self, test, notification):
        """Called when a notification has occurred."""
        notification.elapsed = time.time() - self._start_at
        self.results.append(notification)
        self._notify("notification", notification)

    def add_success(self, test):
        "Called when a test has completed successfully"
        success = Success(test)
        success.elapsed = time.time() - self._start_at
        self.results.append(success)
        self._notify("success", success)

    def pend_test(self, test, pending):
        """Called when a test is pended."""
        pending.elapsed = time.time() - self._start_at
        self.results.append(pending)
        self._notify("pending", pending)

    def omit_test(self, test, omission):
        """Called when a test is omitted."""
        omission.elapsed = time.time() - self._start_at
        self.results.append(omission)
        self._notify("omission", omission)

    def interrupt(self):
        "Indicates that the tests should be interrupted"
        self.interrupted = True

    def need_interrupt(self):
        return self.interrupted

    def succeeded(self):
        return len(list(filter(lambda fault: fault.critical, self.faults))) == 0
    succeeded = property(succeeded)

    def _notify(self, name, *args):
        for listener in self.listeners:
            callback_name = "on_%s" % name
            if hasattr(listener, callback_name):
                getattr(listener, callback_name)(self, *args)

    def summary(self):
        return ("%d test(s), %d assertion(s), %d failure(s), %d error(s), " \
                    "%d pending(s), %d omission(s), %d notification(s)") % \
            (self.n_tests, self.n_assertions, self.n_failures, self.n_errors,
             self.n_pendings, self.n_omissions, self.n_notifications)

    __str__ = summary
