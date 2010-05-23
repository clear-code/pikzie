import pikzie
import pikzie.module_base
from test.utils import Assertions, collect_fault_info

fixture_dir = "test/fixtures/module_based_test_cases"

def test_assertions():
    prefix = 'test_module_based_test_case_fixture'
    assert_result(True, 0, 0, 0, 0, 0, 0, [],
                  test_case_names=["/test_never_match/"])
    assert_result(False, 2, 2, 1, 0, 0, 0,
                  [['F',
                    prefix + '.test_assert_equal_fail',
                    "expected: <2>\n"
                    " but was: <1>",
                    None]],
                  test_case_names=["/test_module_based_test_case_fixture/"])

def assert_result(succeeded, n_tests, n_assertions, n_failures,
                  n_errors, n_pendings, n_notifications, fault_info,
                  **kw_args):
    context = pikzie.TestRunnerContext()
    _kw_args = {"base_dir": fixture_dir, "priority_mode": False}
    for name in kw_args:
        _kw_args[name] = kw_args[name]
    # _kw_args.update(**kw_args) # require Python >= 2.4
    loader = pikzie.TestLoader(**_kw_args)
    test_suite = loader.create_test_suite()
    test_suite.run(context)

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
