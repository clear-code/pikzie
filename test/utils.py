import pikzie

class Assertions(object):
    def assert_result(self, n_tests, n_assertions, n_failures, n_errors,
                      fault_info, tests):
        result = pikzie.TestResult()
        for test_name in tests:
            self.TestCase(test_name).run(result)

        def collect_fault_info(fault):
            return (fault.single_character_display(),
                    str(fault.test),
                    str(fault.detail),
                    fault.test.metadata)

        self.assert_equal([[n_tests, n_assertions, n_failures, n_errors],
                           fault_info],
                          [[result.n_tests, result.n_assertions,
                            result.n_failures, result.n_errors],
                           map(collect_fault_info, result.faults)])

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
            "%s" \
            "Finished in %.3f seconds\n" \
            "\n" \
            "%d test(s), %d assertion(s), %d failure(s), %d error(s)\n"
        self.assert_equal(format % (progress, details, result.elapsed,
                                    n_tests, n_assertions, n_failures, n_errors),
                          message)

