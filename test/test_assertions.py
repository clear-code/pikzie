import os
import re
import shutil
import sys

try:
    from exceptions import *
except ImportError:
    pass

try:
    import syslog
except ImportError:
    pass

import pikzie
import pikzie.pretty_print as pp
import test.utils
try:
    import builtins
except ImportError:
    builtins = __builtins__

base_path = os.path.dirname(__file__)
tmp_path = os.path.join(base_path, "tmp")
nonexistent_path = os.path.join(base_path, "nonexistent")

class TestAssertions(pikzie.TestCase, test.utils.Assertions):
    """Tests for assertions."""

    class ComparableError(Exception):
        def __init__(self, message):
            self.message = message

        def __repr__(self):
            return "%s(%r,)" % (type(self).__name__, self.message)

        def __eq__(self, other):
            return isinstance(other, self.__class__) and \
                    self.message == other.message

    class TestCase(pikzie.TestCase):
        def setup(self):
            shutil.rmtree(tmp_path, True)
            shutil.rmtree(nonexistent_path, True)

        def test_fail(self):
            self.fail("Failed!!!")

        def test_pend(self):
            self.assert_equal(3, 1 + 2)
            self.pend("Pending!!!")
            self.assert_equal(5, 3 + 2)

        def test_notify(self):
            self.assert_equal(3, 1 + 2)
            self.notify("Notification!!!")
            self.assert_equal(5, 3 + 2)

        def test_assert_none(self):
            self.assert_none(None)
            self.assert_none(False)

        def test_assert_none_with_message(self):
            self.assert_none(True, "Message")

        def test_assert_not_none(self):
            self.assert_not_none(False)
            self.assert_not_none(None)

        def test_assert_true_for_none(self):
            self.assert_true(None)

        def test_assert_true_for_boolean(self):
            self.assert_true(True)
            self.assert_true(False)
            self.assert_true(True)

        def test_assert_true_for_integer(self):
            self.assert_true(10)
            self.assert_true(0)
            self.assert_true(-100)

        def test_assert_true_for_string(self):
            self.assert_true("String")
            self.assert_true("")
            self.assert_true("STRING")

        def test_assert_false_for_none(self):
            self.assert_false(None)

        def test_assert_false_for_boolean(self):
            self.assert_false(False)
            self.assert_false(True)
            self.assert_false(False)

        def test_assert_false_for_integer(self):
            self.assert_false(0)
            self.assert_false(10)
            self.assert_false(0)

        def test_assert_false_for_string(self):
            self.assert_false("")
            self.assert_false("STRING")
            self.assert_false("")

        def test_assert_equal(self):
            self.assert_equal(1, 1)
            self.assert_equal(2, 3)
            self.assert_equal(5, 5)

        def test_assert_not_equal(self):
            self.assert_not_equal(2, 3)
            self.assert_not_equal(2, 2)
            self.assert_not_equal(5, 1)

        def test_assert_not_equal_different_repr(self):
            class AlwaysEqual(object):
                def __init__(self, repr):
                    self.repr = repr

                def __ne__(self, other):
                    return False

                def __repr__(self):
                    return repr(self.repr)

            self.assert_not_equal(AlwaysEqual("abc"), AlwaysEqual("aBc"))

        def test_assert_in_delta(self):
            self.assert_in_delta(0.5, 0.5001, 0.01)
            self.assert_in_delta(0.5, 0.5001, 0.001)
            self.assert_in_delta(0.5, 0.5001, 0.0001)
            self.assert_in_delta(0.5, 0.5001, 0.00001)
            self.assert_in_delta(0.5, 0.5001, 0.000001)

        def test_assert_match(self):
            self.assert_match("abc", "abcde")
            self.assert_match("abc", "Xabcde")

        def test_assert_match_re(self):
            self.assert_match(re.compile("xyz"), "xyzabc")
            self.assert_match(re.compile("xyz"), "abcxyz")

        def test_assert_not_match(self):
            self.assert_not_match("abc", "Xabcde")
            self.assert_not_match("abc", "abcde")

        def test_assert_not_match_re(self):
            self.assert_not_match(re.compile("xyz", re.I), "abcXYZ")
            self.assert_not_match(re.compile("xyz", re.I), "XYZabc")

        def test_assert_search(self):
            self.assert_search("bcd", "abcde")
            self.assert_search("bcd", "bcd")
            self.assert_search("bcd", "abCde")

        def test_assert_search_re(self):
            self.assert_search(re.compile("xyz"), "AxyzA")
            self.assert_search(re.compile("xyz"), "xyz")
            self.assert_search(re.compile("xyz"), "AxYzA")

        def test_assert_not_found(self):
            self.assert_not_found("bcd", "abCde")
            self.assert_not_found(re.compile("bcd"), "abCde")
            self.assert_not_found(re.compile("bcd", re.I | re.L), "abCde")

        def test_assert_hasattr(self):
            self.assert_hasattr("string", "ljust")
            self.assert_hasattr("string", "strip")
            self.assert_hasattr("string", "Strip")
            self.assert_hasattr("string", "index")

        def test_assert_callable(self):
            class Callable(object):
                def __call__(self):
                    return "X"

            self.assert_callable(Callable())
            self.assert_callable(lambda : "zzz")
            self.assert_callable("string")
            self.assert_callable(self.test_assert_callable)

        def test_assert_raise_call(self):
            def raise_name_error():
                unknown_name
            exception = self.assert_raise_call(NameError, raise_name_error)
            try:
                unknown_name
            except NameError as name_error:
                expected_message = str(name_error)
            self.assert_equal(expected_message, str(exception))

            def nothing_raised():
                "nothing raised"
            self.assert_raise_call(NameError, nothing_raised)

        def test_assert_raise_call_different_error(self):
            def raise_zero_division_error():
                1 / 0
            self.assert_raise_call(NameError, raise_zero_division_error)

        def test_assert_raise_call_instance(self):
            def raise_error():
                raise TestAssertions.ComparableError("raise error")
            self.assert_raise_call(TestAssertions.ComparableError("raise error"),
                                   raise_error)
            self.assert_raise_call(TestAssertions.ComparableError("not error"),
                                   raise_error)

        def test_assert_nothing_raised_call(self):
            self.assert_equal(123, self.assert_nothing_raised_call(lambda : 123))
            def raise_zero_division_error():
                1 / 0
            self.assert_nothing_raised_call(raise_zero_division_error)

        def test_assert_run_command(self):
            process = self.assert_run_command(["echo", "12345"])
            self.assert_equal(b"12345\n", process.stdout.read())
            self.assert_run_command("false")

        def test_assert_run_command_unknown(self):
            self.assert_run_command(["unknown", "arg1", "arg2"])

        def test_assert_search_syslog_call(self):
            self.assert_search_syslog_call("find me!+",
                                           syslog.syslog, "find me!!!")
            self.assert_search_syslog_call("fix me!",
                                           syslog.syslog, "FIXME!!!")

        def test_assert_exists(self):
            self.assert_exists(__file__)
            self.assert_exists(nonexistent_path)

        def test_assert_not_exists(self):
            self.assert_not_exists(nonexistent_path)
            self.assert_not_exists(__file__)

        def test_assert_open_file(self):
            file = self.assert_open_file(__file__)
            self.assert_equal("r", file.mode)
            file = self.assert_open_file(tmp_path, "w")
            self.assert_equal("w", file.mode)
            self.assert_open_file(nonexistent_path)

        def test_assert_try_call(self):
            self.n = 0
            def succeed_on_5th_try():
                self.n += 1
                self.assert_equal(5, self.n)
            self.assert_try_call(1, 0.01, succeed_on_5th_try)

            def never_succeed():
                self.fail("Never succeed")
            self.assert_try_call(0.1, 0.01, never_succeed)

        def test_assert_kernel_symbol(self):
            address = self.assert_kernel_symbol("printk")
            self.assert_not_none(address)
            self.assert_kernel_symbol("nonexistent")

    def test_fail(self):
        """Test for fail"""
        self.assert_result(False, 1, 0, 1, 0, 0, 0, 0,
                           [("F", "TestCase.test_fail", "Failed!!!", None)],
                           ["test_fail"])

    def test_pend(self):
        self.assert_result(True, 1, 1, 0, 0, 1, 0, 0,
                           [('P',
                             "TestCase.test_pend",
                             "Pending!!!",
                             None)],
                           ["test_pend"])

    def test_notify(self):
        self.assert_result(True, 1, 2, 0, 0, 0, 0, 1,
                           [('N',
                             "TestCase.test_notify",
                             "Notification!!!",
                             None)],
                           ["test_notify"])

    def test_assert_none(self):
        self.assert_result(False, 2, 1, 2, 0, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_none",
                             "expected: <False> is None",
                             None),
                            ("F",
                             "TestCase.test_assert_none_with_message",
                             "Message\n"
                             "expected: <True> is None",
                             None)],
                           ["test_assert_none",
                            "test_assert_none_with_message"])

    def test_assert_not_none(self):
        self.assert_result(False, 1, 1, 1, 0, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_not_none",
                             "expected: not None",
                             None)],
                           ["test_assert_not_none"])

    def test_assert_true(self):
        self.assert_result(False, 4, 3, 4, 0, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_true_for_none",
                             "expected: <None> is a true value",
                             None),
                            ("F",
                             "TestCase.test_assert_true_for_boolean",
                             "expected: <False> is a true value",
                             None),
                            ("F",
                             "TestCase.test_assert_true_for_integer",
                             "expected: <0> is a true value",
                             None),
                            ("F",
                             "TestCase.test_assert_true_for_string",
                             "expected: <''> is a true value",
                             None)],
                           ["test_assert_true_for_none",
                            "test_assert_true_for_boolean",
                            "test_assert_true_for_integer",
                            "test_assert_true_for_string"])

    def test_assert_false(self):
        self.assert_result(False, 4, 4, 3, 0, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_false_for_boolean",
                             "expected: <True> is a false value",
                             None),
                            ("F",
                             "TestCase.test_assert_false_for_integer",
                             "expected: <10> is a false value",
                             None),
                            ("F",
                             "TestCase.test_assert_false_for_string",
                             "expected: <'STRING'> is a false value",
                             None)],
                           ["test_assert_false_for_none",
                            "test_assert_false_for_boolean",
                            "test_assert_false_for_integer",
                            "test_assert_false_for_string"])

    def test_assert_equal(self):
        self.assert_result(False, 1, 1, 1, 0, 0, 0, 0,
                           [('F',
                             'TestCase.test_assert_equal',
                             "expected: <2>\n"
                             " but was: <3>",
                             None)],
                           ["test_assert_equal"])

    def test_assert_not_equal(self):
        self.assert_result(False, 2, 1, 2, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_equal",
                             "not expected: <2>\n"
                             "     but was: <2>",
                             None),
                            ("F",
                             "TestCase.test_assert_not_equal_different_repr",
                             "not expected: <'abc'>\n"
                             "     but was: <'aBc'>\n"
                             "\n"
                             "diff:\n"
                             "- 'abc'\n"
                             "?   ^\n"
                             "+ 'aBc'\n"
                             "?   ^",
                             None)],
                           ["test_assert_not_equal",
                            "test_assert_not_equal_different_repr"])

    def test_assert_in_delta(self):
        expected = 0.5
        actual = 0.5001
        delta = 0.00001
        params = (expected, delta, [expected - delta, expected + delta], actual)
        self.assert_result(False, 1, 3, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_in_delta",
                             "expected: <%r+-%r %r>\n"
                             " but was: <%r>" % params,
                             None)],
                           ["test_assert_in_delta"])

    def test_assert_match(self):
        pattern = re.compile('xyz')
        self.assert_result(False, 2, 2, 2, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_match",
                             "expected: re.match('abc', 'Xabcde') "
                               "doesn't return None\n"
                             " pattern: </abc/>\n"
                             "  target: <'Xabcde'>",
                             None),
                            ('F',
                             "TestCase.test_assert_match_re",
                             "expected: re.match(%s, 'abcxyz') "
                               "doesn't return None\n"
                             " pattern: <%s>\n"
                             "  target: <'abcxyz'>" % \
                                 (pp.format_re_repr(pattern),
                                  pp.format_re(pattern)),
                             None)],
                           ["test_assert_match",
                            "test_assert_match_re"])

    def test_assert_not_match(self):
        pattern = re.compile('xyz', re.IGNORECASE)
        self.assert_result(False, 2, 2, 2, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_match",
                             "expected: re.match('abc', 'abcde') returns None\n"
                             " pattern: </abc/>\n"
                             "  target: <'abcde'>",
                             None),
                            ('F',
                             "TestCase.test_assert_not_match_re",
                             "expected: re.match(%s, 'XYZabc') returns None\n"
                             " pattern: <%s>\n"
                             "  target: <'XYZabc'>" % \
                                 (pp.format_re_repr(pattern),
                                  pp.format_re(pattern)),
                             None)],
                           ["test_assert_not_match",
                            "test_assert_not_match_re"])

    def test_assert_search(self):
        pattern = re.compile('xyz')
        self.assert_result(False, 2, 4, 2, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_search",
                             "expected: re.search('bcd', 'abCde') "
                               "doesn't return None\n"
                             " pattern: </bcd/>\n"
                             "  target: <'abCde'>",
                             None),
                            ('F',
                             "TestCase.test_assert_search_re",
                             "expected: re.search(%s, 'AxYzA') "
                               "doesn't return None\n"
                             " pattern: <%s>\n"
                             "  target: <'AxYzA'>" % \
                                 (pp.format_re_repr(pattern),
                                  pp.format_re(pattern)),
                             None)],
                           ["test_assert_search",
                            "test_assert_search_re"])

    def test_assert_not_found(self):
        pattern = re.compile('bcd', re.IGNORECASE | re.LOCALE)
        self.assert_result(False, 1, 2, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_found",
                             "expected: re.search(%s, 'abCde') returns None\n"
                             " pattern: <%s>\n"
                             "  target: <'abCde'>" % \
                                 (pp.format_re_repr(pattern),
                                  pp.format_re(pattern)),
                             None)],
                           ["test_assert_not_found"])

    def test_assert_hasattr(self):
        self.assert_result(False, 1, 2, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_hasattr",
                             "expected: hasattr('string', 'Strip')",
                             None)],
                           ["test_assert_hasattr"])

    def test_assert_callable(self):
        self.assert_result(False, 1, 2, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_callable",
                             "expected: callable('string')",
                             None)],
                           ["test_assert_callable"])

    def test_assert_raise_call(self):
        zero_division_error = None
        try:
            1 / 0
        except ZeroDivisionError as exception:
            zero_division_error = exception
        self.assert_result(False, 3, 8, 3, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_raise_call",
                             "expected: <%s> is raised\n"
                             " but was: %s() nothing raised" %
                             (NameError,
                              "test_assertions.nothing_raised"),
                             None),
                            ('F',
                             "TestCase.test_assert_raise_call_different_error",
                             "expected: <%s> is raised\n"
                             " but was: <%s>(%s)" %
                             (NameError,
                              type(zero_division_error),
                              zero_division_error),
                             None),
                            ('F',
                             "TestCase.test_assert_raise_call_instance",
                             "expected: <%r>\n"
                             " but was: <%r>" %
                             (self.ComparableError("not error"),
                              self.ComparableError("raise error")),
                             None)],
                           ["test_assert_raise_call",
                            "test_assert_raise_call_different_error",
                            "test_assert_raise_call_instance"])

    def test_assert_nothing_raised_call(self):
        zero_division_error = None
        try:
            1 / 0
        except ZeroDivisionError as exception:
            zero_division_error = exception
        self.assert_result(False, 1, 4, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_nothing_raised_call",
                             "expected: %s() nothing raised\n"
                             " but was: <%s>(%s) is raised" % \
                                 ("test_assertions."
                                  "raise_zero_division_error",
                                  type(zero_division_error),
                                  zero_division_error),
                             None)],
                           ["test_assert_nothing_raised_call"])

    def test_assert_run_command(self):
        try:
            import subprocess
        except ImportError:
            self.pend("subprocess module isn't available.")
        os_error = None
        try:
            subprocess.Popen(["unknown", "arg1", "arg2"])
        except OSError as exception:
            os_error = exception
        self.assert_result(False, 2, 2, 2, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_run_command",
                             "expected: <%s> is successfully finished\n"
                             " but was: <%d> is returned as exit code" % \
                                 ("'false'", 1),
                             None),
                            ('F',
                             "TestCase.test_assert_run_command_unknown",
                             "expected: <%s> is successfully ran\n"
                             " but was: <%s>(%s) is raised and failed to ran" \
                                 % ("['unknown', 'arg1', 'arg2']",
                                    type(os_error),
                                    os_error),
                             None)],
                           ["test_assert_run_command",
                            "test_assert_run_command_unknown"])

    def test_assert_search_syslog_call(self):
        if not hasattr(sys.modules[__name__], "syslog"):
            self.omit("syslog isn't supported on this environment")

        if not os.access("/var/log/messages", os.R_OK):
            self.pend("can't read /var/log/messages.")
        detail = \
            "expected: <%s> is found in <%s>\n" \
            " content: <b?'.*FIXME!!!.*'>" % \
            ("/fix me!/u?", "'/var/log/messages'")
        self.assert_result(False, 1, 2, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_search_syslog_call",
                             re.compile(detail),
                             None)],
                           ["test_assert_search_syslog_call"])

    def test_assert_exists(self):
        self.assert_result(False, 1, 0, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_exists",
                             "expected: <%s> exists" % nonexistent_path,
                             None)],
                           ["test_assert_exists"])

    def test_assert_not_exists(self):
        self.assert_result(False, 1, 0, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_exists",
                             "expected: <%s> doesn't exists" % __file__,
                             None)],
                           ["test_assert_not_exists"])

    def test_assert_open_file(self):
        file_not_found_error = getattr(builtins, "FileNotFoundError", IOError)
        self.assert_result(False, 1, 2, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_open_file",
                             "expected: open('%s') succeeds\n"
                             " but was: <%s>(%s) is raised" % \
                                 (nonexistent_path,
                                  file_not_found_error,
                                  "[Errno 2] No such file or directory: '%s'" % \
                                      nonexistent_path),
                             None)],
                           ["test_assert_open_file"])

    def test_try_call(self):
        self.assert_result(False, 1, 1, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_try_call",
                             "expected: %s succeeds\n"
                             " timeout: <0.1> seconds\n"
                             "interval: <0.01> seconds\n"
                             " but was:\n"
                             "Never succeed" % \
                                 ("test_assertions.never_succeed()",),
                             None)],
                           ["test_assert_try_call"])

    def test_kernel_symbol(self):
        if not hasattr(os, "uname"):
            self.omit("only for Linux environment")
        if os.uname()[0] != "Linux":
            self.omit("only for Linux environment")
        if not os.path.exists("/proc/kallsyms"):
            self.omit("require /proc/kallsyms")
        self.assert_result(False, 1, 1, 1, 0, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_kernel_symbol",
                             "expected: <'nonexistent'> is in kernel symbols",
                             None)],
                           ["test_assert_kernel_symbol"])
