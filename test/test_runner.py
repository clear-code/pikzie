from StringIO import StringIO
import re
import pikzie
import pikzie.ui.text

class TestRunner(pikzie.TestCase):
    def setup(self):
        self.output = StringIO()
        self.runner = pikzie.ui.text.TextTestRunner(self.output, use_color=False)
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
            "1) Failure: TestCase.test_fail_assertion: %s\n" \
            "expected: <'aaaaa'>\n" \
            " but was: <'a'>\n" \
            "diff:\n" \
            "- 'aaaaa'\n" \
            "+ 'a'\n" \
            "%s:%d: test_fail_assertion(): %s\n" \
            "\n"
        target_line = "self.assert_equal(\"aaaaa\", \"a\")"
        line_no = self._find_target_line_no(target_line)
        details = format % (target_line, self.file_name, line_no, target_line)
        self.assert_output("F", 1, 1, 1, 0, details, [test])

    def test_run_error_test(self):
        class TestCase(pikzie.TestCase):
            def test_error_raised(self):
                self.unknown_method(12345)
                self.assert_equal(3, 1 + 2)

        test = TestCase("test_error_raised")
        format = \
            "1) Error: TestCase.test_error_raised\n" \
            "exceptions.AttributeError: " \
            "'TestCase' object has no attribute 'unknown_method'\n" \
            "%s:%d: test_error_raised(): %s\n" \
            "\n"
        target_line = "self.unknown_method(12345)"
        line_no = self._find_target_line_no(target_line)
        details = format % (self.file_name, line_no, target_line)
        self.assert_output("E", 1, 0, 0, 1, details, [test])

    def assert_success_output(self, n_tests, n_assertions, tests):
        self.assert_output("." * n_tests, n_tests, n_assertions, 0, 0, "", tests)

    def assert_output(self, progress, n_tests, n_assertions, n_failures,
                      n_errors, details, tests):
        suite = pikzie.TestSuite(tests)
        result = self.runner.run(suite)
        self.assert_equal(n_tests, result.n_tests)
        self.assert_equal(n_assertions, result.n_assertions)
        self.assert_equal(n_failures, result.n_failures)
        self.assert_equal(n_errors, result.n_errors)
        self.output.seek(0)
        message = self.output.read()
        format = \
            "%s\n" \
            "\n" \
            "%s" \
            "Finished in 0.000 seconds\n" \
            "\n" \
            "%d test(s), %d assertion(s), %d failure(s), %d error(s)\n"
        self.assert_equal(format % (progress, details,
                                    n_tests, n_assertions, n_failures, n_errors),
                          message)

    def _find_target_line_no(self, pattern):
        line_no = -1
        if type(pattern) == type(""):
            pattern = re.compile(re.escape(pattern))
        try:
            f = file(self.file_name)
            for i, line in enumerate(f):
                if pattern.search(line):
                    line_no = i + 1
                    break
        finally:
            f.close()
        return line_no
