import pikzie
import pikzie.module_base
from test.utils import Assertions

fixture_dir = "test/fixtures/module_based_test_cases"
pattern = fixture_dir + "/test_*.py"

def test_assertions():
    prefix = 'test.fixtures.module_based_test_cases.test_assertions'
    assert_result(False, 2, 2, 1, 0, 0, 0,
                  [['F',
                    prefix + '.test_assert_equal_fail',
                    "expected: <2>\n"
                    " but was: <1>",
                    None]],
                  test_case_names=["/test_assertions/"])

def assert_result(succeeded, n_tests, n_assertions, n_failures,
                  n_errors, n_pendings, n_notifications, fault_info,
                  **kw_args):
    context = pikzie.TestRunnerContext()
    _kw_args = {"pattern": pattern, "priority_mode": False}
    _kw_args.update(**kw_args)
    loader = pikzie.TestLoader(**_kw_args)
    test_suite = loader.create_test_suite()
    test_suite.run(context)

    def collect_fault_info(fault):
        return (fault.symbol,
                str(fault.test),
                str(fault.message),
                fault.test.metadata)

    assert_equal(Assertions.RegexpMatchResult(succeeded,
                                              (n_tests,
                                               n_assertions,
                                               n_failures,
                                               n_errors,
                                               n_pendings,
                                               n_notifications),
                                              fault_info),
                 Assertions.RegexpMatchResult(context.succeeded,
                                              (context.n_tests,
                                               context.n_assertions,
                                               context.n_failures,
                                               context.n_errors,
                                               context.n_pendings,
                                               context.n_notifications),
                                              map(collect_fault_info,
                                                  context.faults)))
