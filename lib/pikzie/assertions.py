import os
import sys
import re
import difflib
import traceback
import subprocess
import random
import syslog
import select

if not hasattr(os, "SEEK_END"):
    os.SEEK_END = 2

import pikzie.pretty_print as pp

class Assertions(object):
    def fail(self, message):
        """Always fails with message.

        self.fail("must not happen!") # => fail
        """
        self._fail(message)

    def pend(self, message):
        """Pending the current running test.

        self.pend("module XXX isn't found") # => pend test
        """
        self._pend(message)

    def notify(self, message):
        """Notify a message for the current running test.

        if command_not_found:
            self.notify("skip due to command not found") # => notify a message
            return
        """
        self._notify(message)

    def assert_none(self, expression, message=None):
        """Passes if expression is None.

        self.assert_none(None) # => pass
        """
        if expression is None:
            self._pass_assertion()
        else:
            system_message = "expected: <%r> is None" % expression
            self._fail(system_message, message)

    def assert_not_none(self, expression, message=None):
        """Passes if expression is not None.

        self.assert_not_none("not none") # => pass
        """
        if expression is not None:
            self._pass_assertion()
        else:
            self._fail("expected: not None", message)

    def assert_true(self, expression, message=None):
        """Passes if expression is true value.

        self.assert_true(True)     # => pass
        self.assert_true("string") # => pass
        """
        if expression:
            self._pass_assertion()
        else:
            system_message = "expected: <%r> is a true value" % expression
            self._fail(system_message, message)

    def assert_false(self, expression, message=None):
        """Passes if expression is false value.

        self.assert_false(False) # => pass
        self.assert_false("")    # => pass
        """
        if expression:
            system_message = "expected: <%r> is a false value" % expression
            self._fail(system_message, message)
        else:
            self._pass_assertion()

    def assert_equal(self, expected, actual, message=None):
        """Passes if expected == actual.

        self.assert_equal(5, 2 + 3) # => pass
        """
        if expected == actual:
            self._pass_assertion()
        else:
            expected = pp.format(expected)
            actual = pp.format(actual)
            diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
            system_message = "expected: <%s>\n but was: <%s>\ndiff:\n%s" % \
                (expected, actual, "\n".join(diff))
            self._fail(system_message, message)

    def assert_not_equal(self, not_expected, actual, message=None):
        """Passes if not_expected != actual.

        self.assert_equal(-5, 2 + 3) # => pass
        """
        if not_expected != actual:
            self._pass_assertion()
        else:
            not_expected = pp.format(not_expected)
            actual = pp.format(actual)
            system_message = "not expected: <%s>\n     but was: <%s>" % \
                (not_expected, actual)
            if not_expected != actual:
                diff = difflib.ndiff(not_expected.splitlines(),
                                     actual.splitlines())
                system_message = "%s\ndiff:\n%s" % \
                    (system_message, "\n".join(diff))
            self._fail(system_message, message)

    def assert_in_delta(self, expected, actual, delta, message=None):
        """Passes if (expected - delta) <= actual <= (expected + delta).

        self.assert_in_delta(3, 3.01, 0.001) # => pass
        """
        lower = expected - delta
        upper = expected + delta
        if lower <= actual <= upper:
            self._pass_assertion()
        else:
            expected = pp.format(expected)
            actual = pp.format(actual)
            delta = pp.format(delta)
            range = pp.format([lower, upper])
            system_message = "expected: <%s+-%s %s>\n but was: <%s>" % \
                (expected, delta, range, actual)
            self._fail(system_message, message)

    def assert_match(self, pattern, target, message=None):
        """Passes if re.match(pattern, target) doesn't return None.

        self.assert_match("abc", "abcde") # => pass
        self.assert_match("abc", "deabc") # => fail
        """
        if re.match(pattern, target):
            self._pass_assertion()
        else:
            pattern_repr = pp.format_re_repr(pattern)
            pattern = pp.format_re(pattern)
            target = pp.format(target)
            format = \
                "expected: re.match(%s, %s) doesn't return None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_not_match(self, pattern, target, message=None):
        """Passes if re.match(pattern, target) returns None.

        self.assert_not_match("abc", "deabc") # => pass
        self.assert_not_match("abc", "abcde") # => fail
        """
        if re.match(pattern, target) is None:
            self._pass_assertion()
        else:
            pattern_repr = pp.format_re_repr(pattern)
            pattern = pp.format_re(pattern)
            target = pp.format(target)
            format = \
                "expected: re.match(%s, %s) returns None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_search(self, pattern, target, message=None):
        """Passes if re.search(pattern, target) doesn't return None.

        self.assert_search("abc", "deabc") # => pass
        self.assert_search("abc", "deABC") # => fail
        """
        if re.search(pattern, target):
            self._pass_assertion()
        else:
            pattern_repr = pp.format_re_repr(pattern)
            pattern = pp.format_re(pattern)
            target = pp.format(target)
            format = \
                "expected: re.search(%s, %s) doesn't return None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_not_found(self, pattern, target, message=None):
        """Passes if re.search(pattern, target) returns None.

        self.assert_search("abc", "deABC") # => pass
        self.assert_search("abc", "deabc") # => fail
        """
        if re.search(pattern, target) is None:
            self._pass_assertion()
        else:
            pattern_repr = pp.format_re_repr(pattern)
            pattern = pp.format_re(pattern)
            target = pp.format(target)
            format = \
                "expected: re.search(%s, %s) returns None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_hasattr(self, object, name, message=None):
        """Passes if hasattr(object, name) returns True.

        self.assert_hasattr("string", "strip")   # => pass
        self.assert_hasattr("string", "unknown") # => fail
        """
        if hasattr(object, name):
            self._pass_assertion()
        else:
            object = pp.format(object)
            name = pp.format(name)
            system_message = "expected: hasattr(%s, %s)" % (object, name)
            self._fail(system_message, message)

    def assert_callable(self, object, message=None):
        """Passes if callable(object) returns True.

        self.assert_callable(lambda: 1) # => pass
        self.assert_callable("string")  # => fail
        """
        if callable(object):
            self._pass_assertion()
        else:
            object = pp.format(object)
            system_message = "expected: callable(%s)" % (object)
            self._fail(system_message, message)

    def assert_call_raise(self, exception, callable_object, *args, **kw_args):
        """Passes if callable_object(*args, **kw_args) raises exception and
        returns raised exception value.

        self.assert_call_raise(NameError,
                               lambda: unknown_variable) # => pass
                                                         # => returns NameError
                                                         #    value
        self.assert_call_raise(NameError, lambda: 1)     # => fail
        """
        self.assert_callable(callable_object)
        try:
            callable_object(*args, **kw_args)
        except exception:
            self._pass_assertion()
            return sys.exc_info()[1]
        except:
            actual = sys.exc_info()
            actual_exception_class, actual_exception_value = actual[:2]
            message = \
                "expected: <%s> is raised\n" \
                " but was: <%s>(%s)" % \
                (pp.format_exception_class(exception),
                 pp.format_exception_class(actual_exception_class),
                 str(actual_exception_value))
            self._fail(message)
        else:
            message = \
                "expected: <%s> is raised\n" \
                " but was: %s(*%s, **%s) nothing raised" % \
                (pp.format_exception_class(exception),
                 pp.format_callable_object(callable_object),
                 pp.format(args),
                 pp.format(kw_args))
            self._fail(message)

    def assert_call_nothing_raised(self, callable_object, *args, **kw_args):
        """Passes if callable_object(*args, **kw_args) raises nothing exception
        and returns called result.

        self.assert_call_nothing_raised(lambda: 1)                # => pass
                                                                  # => returns 1
        self.assert_call_nothing_raised(lambda: unknown_variable) # => fail
        """
        self.assert_callable(callable_object)
        try:
            result = callable_object(*args, **kw_args)
        except:
            actual = sys.exc_info()[:2]
            actual_exception_class, actual_exception_value = actual
            message = \
                "expected: %s(*%s, **%s) nothing raised\n" \
                " but was: <%s>(%s) is raised" % \
                (pp.format_callable_object(callable_object),
                 pp.format(args),
                 pp.format(kw_args),
                 pp.format_exception_class(actual_exception_class),
                 str(actual_exception_value))
            self._fail(message)
        self._pass_assertion()
        return result

    def assert_run_command(self, command, **kw_args):
        """Passes if command is successfully ran and returns subprocess.Popen.

        process = self.assert_run_command(["echo", "123"])    # => pass
        self.assert_equal("123\n", process.stdout.read())     # => pass
        self.assert_run_command("false")                      # => fail
        self.assert_run_command("unknown-command")            # => fail
        """
        popen_kw_args = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }
        popen_kw_args.update(kw_args)
        try:
            process = subprocess.Popen(command, **popen_kw_args)
        except OSError:
            exception_class, exception_value = sys.exc_info()[:2]
            message = "expected: <%s> is successfully ran\n" \
                " but was: <%s>(%s) is raised and failed to ran" % \
                (pp.format(command),
                 pp.format_exception_class(exception_class),
                 str(exception_value))
            self._fail(message)
        return_code = process.wait()
        if return_code != 0:
            message = "expected: <%s> is successfully finished\n" \
                " but was: failed with %d return code" % \
                (pp.format(command), return_code)
            self._fail(message)
        self._pass_assertion()
        return process

    def assert_search_syslog(self, pattern, callable_object, *args, **kw_args):
        """Passes if re.search(pattern, SYSLOG_CONTENT) doesn't return None.

        self.assert_search_syslog("abc", syslog.syslog, "abc") # => pass
        self.assert_search_syslog("abc", syslog.syslog, "xyz") # => fail
        """
        self.assert_callable(callable_object)

        log_file = "/var/log/messages"
        messages = open(log_file)
        messages.seek(0, os.SEEK_END)

        mark = 'Pikzie: %.20f' % random.random()
        syslog.syslog(mark)

        def search(pattern):
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            lines = []
            while len(select.select([messages], [], [], 1)[0]) > 0:
                line = messages.readline()
                if len(line) == 0:
                    break
                lines.append(line)
                if re.search(pattern, line):
                    return
            message = \
                "expected: <%s> is found in <%s>\n" \
                "  target: <%s>" % \
                (pp.format_re(pattern),
                 pp.format(log_file),
                 pp.format(''.join(lines)))
            self.fail(message)

        search(re.escape(mark))
        result = callable_object(*args, **kw_args)
        search(pattern)
