from StringIO import StringIO
import re

import pikzie
from pikzie.ui.console import ConsoleTestRunner

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
            "diff:\n" \
            "- aaaaa\n" \
            "+ a\n" \
            "\n"
        target_line = "self.assert_equal(\"aaaaa\", \"a\")"
        line_no = Source.find_target_line_no(target_line)
        details = format % (target_line, self.file_name, line_no, target_line)
        self.assert_output("F", 1, 1, 1, 0, 0, 0, details, [test])

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
            "exceptions.AttributeError: " \
            "'TestCase' object has no attribute 'unknown_method'\n" \
            "\n"
        target_line = "self.unknown_method(12345)"
        line_no = Source.find_target_line_no(target_line)
        details = format % (self.file_name, line_no, target_line)
        self.assert_output("E", 1, 0, 0, 1, 0, 0, details, [test])

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
            "exceptions.AttributeError: " \
            "'TestCase' object has no attribute 'unknown_attribute'\n" \
            "\n" \
            "2) Failure: TestCase.test_with_metadata: %s\n" \
            "  bug: 999\n" \
            "  key: value\n" \
            "%s:%d: %s\n" \
            "expected: <3>\n" \
            " but was: <-1>\n" \
            "diff:\n" \
            "- 3\n" \
            "+ -1\n" \
            "\n"
        target_line1 = "self.unknown_attribute"
        line_no1 = Source.find_target_line_no(target_line1)
        target_line2 = "self.assert_equal(3, 1 - 2)"
        line_no2 = Source.find_target_line_no(target_line2)
        details = format % (self.file_name, line_no1, target_line1,
                            target_line2, self.file_name, line_no2, target_line2)
        self.assert_output("EF", 2, 0, 1, 1, 0, 0, details, tests)

    def test_run_pending_test(self):
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
        self.assert_output("P", 1, 0, 0, 0, 1, 0, details, [test])

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
        self.assert_output("N.", 1, 2, 0, 0, 0, 1, details, [test])
