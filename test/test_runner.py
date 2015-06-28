import re

try:
    from exceptions import *
except ImportError:
    pass

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pikzie
from pikzie.ui.console import ConsoleTestRunner
import pikzie.pretty_print as pp

from test.utils import *

class TestRunner(pikzie.TestCase, Assertions):
    def setup(self):
        self.output = StringIO()
        self.runner = ConsoleTestRunner(self.output, use_color=False)
        self.file_name = __file__
        if self.file_name.endswith("pyc"):
            self.file_name = self.file_name[:-1]

    def test_run_empty_test(self):
        class TestCase(pikzie.TestCase):
            def test_nothing(self):
                pass
        test = TestCase("test_nothing")
        self.assert_success_output(1, 0, [test])

    def test_run_test_with_assertions(self):
        class TestCase(pikzie.TestCase):
            def test_assertion(self):
                self.assert_equal(3, 1 + 2)
                self.assert_equal("aaaaa", "a" * 5)

        test = TestCase("test_assertion")
        self.assert_success_output(1, 2, [test])

    def test_run_failed_test(self):
        class TestCase(pikzie.TestCase):
            def test_fail_assertion(self):
                self.assert_equal(3, 1 + 2)
                self.assert_equal("aaaaa", "a")

        test = TestCase("test_fail_assertion")
        format = \
            "\n" \
            "1) Failure: TestCase.test_fail_assertion: %s\n" \
            "%s:%d: %s\n" \
            "expected: <'aaaaa'>\n" \
            " but was: <'a'>\n" \
            "\n"
        target_line = "self.assert_equal(\"aaaaa\", \"a\")"
        line_no = Source.find_target_line_no(target_line)
        details = format % (target_line, self.file_name, line_no, target_line)
        self.assert_output("F", 1, 1, 1, 0, 0, 0, 0, details, [test])

    def test_run_error_test(self):
        class TestCase(pikzie.TestCase):
            def test_error_raised(self):
                self.unknown_method(12345)
                self.assert_equal(3, 1 + 2)

        test = TestCase("test_error_raised")
        format = \
            "\n" \
            "1) Error: TestCase.test_error_raised\n" \
            "%s:%d: %s\n" \
            "%s: " \
            "'TestCase' object has no attribute 'unknown_method'\n" \
            "\n"
        target_line = "self.unknown_method(12345)"
        line_no = Source.find_target_line_no(target_line)
        details = format % (self.file_name, line_no, target_line,
                            AttributeError)
        self.assert_output("E", 1, 0, 0, 1, 0, 0, 0, details, [test])

    def test_metadata(self):
        class TestCase(pikzie.TestCase):
            def test_error_raised(self):
                self.unknown_attribute
                self.assert_equal(3, 1 + 2)
            test_error_raised = pikzie.bug(123)(test_error_raised)

            def test_with_metadata(self):
                self.assert_equal(3, 1 - 2)
            test_with_metadata = pikzie.bug(999)(test_with_metadata)
            test_with_metadata = \
                pikzie.metadata("key", "value")(test_with_metadata)

        tests = [TestCase("test_error_raised"),
                 TestCase("test_with_metadata")]
        format = \
            "\n" \
            "1) Error: TestCase.test_error_raised\n" \
            "  bug: 123\n" \
            "%s:%d: %s\n" \
            "%s: " \
            "'TestCase' object has no attribute 'unknown_attribute'\n" \
            "\n" \
            "2) Failure: TestCase.test_with_metadata: %s\n" \
            "  bug: 999\n" \
            "  key: value\n" \
            "%s:%d: %s\n" \
            "expected: <3>\n" \
            " but was: <-1>\n" \
            "\n"
        target_line1 = "self.unknown_attribute"
        line_no1 = Source.find_target_line_no(target_line1)
        target_line2 = "self.assert_equal(3, 1 - 2)"
        line_no2 = Source.find_target_line_no(target_line2)
        details = format % (self.file_name, line_no1, target_line1,
                            AttributeError,
                            target_line2, self.file_name, line_no2, target_line2)
        self.assert_output("EF", 2, 0, 1, 1, 0, 0, 0, details, tests)

    def test_pending(self):
        class TestCase(pikzie.TestCase):
            def test_pend(self):
                self.pend("just a minute!")

        test = TestCase("test_pend")
        format = \
            "\n" \
            "1) Pending: TestCase.test_pend: just a minute!\n" \
            "%s:%d: %s\n" \
            "\n"
        target_line = "self.pend(\"just a minute!\")"
        line_no = Source.find_target_line_no(target_line)
        details = format % (self.file_name, line_no, target_line)
        self.assert_output("P", 1, 0, 0, 0, 1, 0, 0, details, [test])

    def test_omission(self):
        class TestCase(pikzie.TestCase):
            def test_omit(self):
                self.omit("just a minute!")

        test = TestCase("test_omit")
        format = \
            "\n" \
            "1) Omission: TestCase.test_omit: just a minute!\n" \
            "%s:%d: %s\n" \
            "\n"
        target_line = "self.omit(\"just a minute!\")"
        line_no = Source.find_target_line_no(target_line)
        details = format % (self.file_name, line_no, target_line)
        self.assert_output("O", 1, 0, 0, 0, 0, 1, 0, details, [test])

    def test_notification(self):
        class TestCase(pikzie.TestCase):
            def test_notify(self):
                self.assert_equal(1, 3 - 2)
                self.notify("Call me!")
                self.assert_equal(5, 3 + 2)

        test = TestCase("test_notify")
        format = \
            "\n" \
            "1) Notification: TestCase.test_notify: Call me!\n" \
            "%s:%d: %s\n" \
            "\n"
        target_line = "self.notify(\"Call me!\")"
        line_no = Source.find_target_line_no(target_line)
        details = format % (self.file_name, line_no, target_line)
        self.assert_output("N.", 1, 2, 0, 0, 0, 0, 1, details, [test])

    def test_run_failed_tuple_data(self):
        class TestCase(pikzie.TestCase):
            def test_fail_assertion_tuple_data(self, data):
                self.assert_equal(data, data)
                self.assert_equal("tuple", data)
        label = "fail"
        data = (1, 2)
        test = TestCase("test_fail_assertion_tuple_data", label, data)
        format = \
            "\n" \
            "1) Failure: TestCase.test_fail_assertion_tuple_data (%s): %s\n" \
            "  data: %s\n" \
            "%s:%d: %s\n" \
            "expected: <'tuple'>\n" \
            " but was: <%s>\n" \
            "\n"
        target_line = "self.assert_equal(\"tuple\", data)"
        line_no = Source.find_target_line_no(target_line)
        details = format % (label, target_line, str(data),
                            self.file_name, line_no, target_line, str(data))
        self.assert_output("F", 1, 1, 1, 0, 0, 0, 0, details, [test])

    def test_run_failed_list_data(self):
        class TestCase(pikzie.TestCase):
            def test_fail_assertion_list_data(self, data):
                self.assert_equal(data, data)
                self.assert_equal("list", data)
        label = "fail"
        data = [1, 2]
        test = TestCase("test_fail_assertion_list_data", label, data)
        format = \
            "\n" \
            "1) Failure: TestCase.test_fail_assertion_list_data (%s): %s\n" \
            "  data: %s\n" \
            "%s:%d: %s\n" \
            "expected: <'list'>\n" \
            " but was: <%s>\n" \
            "\n"
        target_line = "self.assert_equal(\"list\", data)"
        line_no = Source.find_target_line_no(target_line)
        details = format % (label, target_line, str(data),
                            self.file_name, line_no, target_line, str(data))
        self.assert_output("F", 1, 1, 1, 0, 0, 0, 0, details, [test])

    def test_run_failed_dict_data(self):
        class TestCase(pikzie.TestCase):
            def test_fail_assertion_dict_data(self, data):
                self.assert_equal(data, data)
                self.assert_equal("dict", data)
        label = "fail"
        data = {"a": 1, "b": 2}
        test = TestCase("test_fail_assertion_dict_data", label, data)
        format = \
            "\n" \
            "1) Failure: TestCase.test_fail_assertion_dict_data (%s): %s\n" \
            "  data: %s\n" \
            "%s:%d: %s\n" \
            "expected: <'dict'>\n" \
            " but was: <%s>\n" \
            "\n"
        target_line = "self.assert_equal(\"dict\", data)"
        line_no = Source.find_target_line_no(target_line)
        details = format % (label, target_line, str(data),
                            self.file_name, line_no, target_line,
                            pp.format(data))
        self.assert_output("F", 1, 1, 1, 0, 0, 0, 0, details, [test])

