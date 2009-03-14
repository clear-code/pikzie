import os
import sys
import re
import traceback
import random
import syslog
import select
import time
import popen2
import signal
import fcntl

import pikzie.core
import pikzie.pretty_print as pp

class Assertions(object):
    def fail(self, message):
        """
        Always fails with message.

          self.fail("must not happen!") # => fail
        """
        self._fail(message)

    def pend(self, message):
        """
        Pending the current running test.

          self.pend("module XXX isn't found") # => pend test
        """
        self._pend(message)

    def notify(self, message):
        """
        Notify a message for the current running test.

          if command_not_found:
              self.notify("skip due to command not found") # => notify a message
              return
        """
        self._notify(message)

    def assert_none(self, expression, message=None):
        """
        Passes if expression is None.

          self.assert_none(None) # => pass
        """
        if expression is None:
            self._pass_assertion()
        else:
            system_message = "expected: <%r> is None" % expression
            self._fail(system_message, message)

    def assert_not_none(self, expression, message=None):
        """
        Passes if expression is not None.

          self.assert_not_none("not none") # => pass
        """
        if expression is not None:
            self._pass_assertion()
        else:
            self._fail("expected: not None", message)

    def assert_true(self, expression, message=None):
        """
        Passes if expression is true value.

          self.assert_true(True)     # => pass
          self.assert_true("string") # => pass
        """
        if expression:
            self._pass_assertion()
        else:
            system_message = "expected: <%r> is a true value" % expression
            self._fail(system_message, message)

    def assert_false(self, expression, message=None):
        """
        Passes if expression is false value.

          self.assert_false(False) # => pass
          self.assert_false("")    # => pass
        """
        if expression:
            system_message = "expected: <%r> is a false value" % expression
            self._fail(system_message, message)
        else:
            self._pass_assertion()

    def assert_equal(self, expected, actual, message=None):
        """
        Passes if expected == actual.

          self.assert_equal(5, 2 + 3) # => pass
        """
        if expected == actual:
            self._pass_assertion()
        else:
            formatted_expected = pp.format(expected)
            formatted_actual = pp.format(actual)
            system_message = "expected: <%s>\n but was: <%s>" % \
                (formatted_expected, formatted_actual)
            system_message = pp.append_diff(system_message, expected, actual)
            self._fail(system_message, message)

    def assert_not_equal(self, not_expected, actual, message=None):
        """
        Passes if not_expected != actual.

          self.assert_equal(-5, 2 + 3) # => pass
        """
        if not_expected != actual:
            self._pass_assertion()
        else:
            formatted_not_expected = pp.format(not_expected)
            formatted_actual = pp.format(actual)
            system_message = "not expected: <%s>\n     but was: <%s>" % \
                (formatted_not_expected, formatted_actual)
            if formatted_not_expected != formatted_actual:
                system_message = pp.append_diff(system_message,
                                                not_expected, actual)
            self._fail(system_message, message)

    def assert_in_delta(self, expected, actual, delta, message=None):
        """
        Passes if (expected - delta) <= actual <= (expected + delta).

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
        """
        Passes if re.match(pattern, target) doesn't return None.

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
        """
        Passes if re.match(pattern, target) returns None.

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
        """
        Passes if re.search(pattern, target) doesn't return None.

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
        """
        Passes if re.search(pattern, target) returns None.

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
        """
        Passes if hasattr(object, name) returns True.

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
        """
        Passes if callable(object) returns True.

          self.assert_callable(lambda: 1) # => pass
          self.assert_callable("string")  # => fail
        """
        if callable(object):
            self._pass_assertion()
        else:
            object = pp.format(object)
            system_message = "expected: callable(%s)" % (object)
            self._fail(system_message, message)

    def assert_raise_call(self, exception, callable_object, *args, **kw_args):
        """
        Passes if callable_object(*args, **kw_args) raises exception and
        returns raised exception value.

          self.assert_raise_call(NameError,
                                 lambda: unknown_variable) # => pass
                                                           # => returns NameError
                                                           #    value
          self.assert_raise_call(NameError, lambda: 1)     # => fail
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
                " but was: %s nothing raised" % \
                (pp.format_exception_class(exception),
                 pp.format_call(callable_object, args, kw_args))
            self._fail(message)

    def assert_call_raise(self, *args, **kw_args):
        """Deprecated. Use assert_raise_call()."""
        self.notify("assert_call_raise() is deprecated. "
                    "Use assert_raise_call() instead.")
        return self.assert_raise_call(*args, **kw_args)

    def assert_nothing_raised_call(self, callable_object, *args, **kw_args):
        """
        Passes if callable_object(*args, **kw_args) raises nothing exception
        and returns called result.

          self.assert_nothing_raised_call(lambda: 1)                # => pass
                                                                    # => returns 1
          self.assert_nothing_raised_call(lambda: unknown_variable) # => fail
        """
        self.assert_callable(callable_object)
        try:
            result = callable_object(*args, **kw_args)
        except:
            actual = sys.exc_info()[:2]
            actual_exception_class, actual_exception_value = actual
            message = \
                "expected: %s nothing raised\n" \
                " but was: <%s>(%s) is raised" % \
                (pp.format_call(callable_object, args, kw_args),
                 pp.format_exception_class(actual_exception_class),
                 str(actual_exception_value))
            self._fail(message)
        self._pass_assertion()
        return result

    def assert_call_nothing_raised(self, *args, **kw_args):
        """Deprecated. Use assert_nothing_raised_call()."""
        self.notify("assert_call_nothing_raised() is deprecated. "
                    "Use assert_nothing_raised_call() instead.")
        return self.assert_nothing_raised_call(*args, **kw_args)

    def assert_run_command(self, command, **kw_args):
        """
        Passes if command is successfully ran and returns subprocess.Popen.

          process = self.assert_run_command(["echo", "123"])    # => pass
          self.assert_equal("123\\n", process.stdout.read())    # => pass
          self.assert_run_command("false")                      # => fail
          self.assert_run_command("unknown-command")            # => fail
        """
        import subprocess
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
                " but was: <%d> is returned as exit code" % \
                (pp.format(command), return_code)
            self._fail(message)
        self._pass_assertion()
        return process

    def assert_search_syslog_call(self, pattern,
                                  callable_object, *args, **kw_args):
        """
        Passes if re.search(pattern, SYSLOG_CONTENT) doesn't return None
        after callable_object(*args, **kw_args).

          self.assert_search_syslog_call("X", syslog.syslog, "XYZ") # => pass
          self.assert_search_syslog_call("X", syslog.syslog, "ABC") # => fail
        """
        self.assert_callable(callable_object)

        mark = 'Pikzie: %.20f' % random.random()
        syslog.syslog(mark)

        log_file = "/var/log/messages"
        messages = popen2.Popen4(["tail", "-F", log_file])
        fd = messages.fromchild.fileno()
        fcntl.fcntl(fd, fcntl.F_SETFL,
                    os.O_NONBLOCK | fcntl.fcntl(fd, fcntl.F_GETFL))

        def search(pattern):
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            content = ''
            timeout = 1.5
            while len(select.select([fd], [], [], timeout)[0]) > 0:
                timeout = 0.1
                added_content = messages.fromchild.read()
                if not added_content:
                    break
                content += added_content
                if re.search(pattern, content):
                    return
            message = \
                "expected: <%s> is found in <%s>\n" \
                " content: <%s>" % \
                (pp.format_re(pattern),
                 pp.format(log_file),
                 pp.format(content))
            self.fail(message)

        try:
            search(re.escape(mark))
            result = callable_object(*args, **kw_args)
            search(pattern)
        finally:
            os.kill(messages.pid, signal.SIGINT)
            messages.wait()

    def assert_open_file(self, name, *args):
        """
        Passes if file(name, *args) succeeds.

          file = self.assert_open_file("/tmp/exist", "w") # => pass
          self.assert_open_file("/tmp/nonexistence")      # => fail
        """
        try:
            result = file(name, *args)
        except IOError:
            exception_class, exception_value = sys.exc_info()[:2]
            message = \
                "expected: file(%s) succeeds\n" \
                " but was: <%s>(%s) is raised" % \
                (pp.format_call_arguments((name,) + args, {}),
                 pp.format_exception_class(exception_class),
                 str(exception_value))
            self._fail(message)
        self._pass_assertion
        return result

    def assert_try_call(self, timeout, interval,
                        callable_object, *args, **kw_args):
        """
        Passes if callable_object(*args, **kw_args) doesn't fail any
        assertions in <timeout> seconds.
        (It will tried <timeout / interval> times.)

          def random_number():
              number = random.randint(0, 9)
              self.assert_in_delta(5, number, 1)
              return number
          self.assert_try_call(1, 0.1, random_number) # => will pass
                                                      # returns 4, 5 or 6
          self.assert_try_call(1, 0.1, self.fail, "Never succeed") # => fail
        """
        rest = timeout
        while True:
            before = time.time()
            try:
                result = callable_object(*args, **kw_args)
                break
            except pikzie.core.AssertionFailure:
                if rest <= 0:
                    message = \
                        "expected: %s succeeds\n" \
                        " timeout: <%s> seconds\n" \
                        "interval: <%s> seconds\n" \
                        " but was:\n%s" % \
                        (pp.format_call(callable_object, args, kw_args),
                         timeout, interval,
                         str(sys.exc_info()[1]))
                    self._fail(message)
                runtime = time.time() - before
                wait_time = interval - runtime
                if wait_time > 0:
                    time.sleep(wait_time)
                rest -= max(runtime, interval)
        self._pass_assertion
        return result

    def assert_kernel_symbol(self, name):
        """
        Passes if /proc/kallsyms can be opened and name is in the list.

          self.assert_kernel_symbol("printk")       # => pass
                                                    # returns an address of printk
          self.assert_kernel_symbol("non_existent") # => fail
        """
        for line in self.assert_open_file("/proc/kallsyms"):
            symbol_info = line.split()
            address = symbol_info[0]
            symbol_name = symbol_info[2]
            if name == symbol_name:
                self._pass_assertion
                return address
        self._fail("expected: <%r> is in kernel symbols" % name)
