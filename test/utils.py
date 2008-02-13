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
