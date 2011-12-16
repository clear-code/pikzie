import os
import pikzie

class TestLoader(pikzie.TestCase):
    """Tests for TestLoader"""

    def setup(self):
        self.fixture_dir = os.path.join("test", "fixtures", "tests")
        self.loader = pikzie.TestLoader(base_dir=self.fixture_dir,
                                        priority_mode=False)

    def test_find_targets(self):
        def build_full_path(name):
            return "test_%s.py" % name
        base_dir, targets = self.loader._find_targets()
        self.assert_equal((os.path.abspath(self.fixture_dir),
                           sorted(map(build_full_path,
                                      ["module_base", "xxx", "yyy", "zzz"]))),
                          (base_dir, sorted(targets)))

    def test_load_modules(self):
        modules = self.loader._load_modules()
        module_names = map(lambda module: module.__name__, modules)
        self.assert_equal(["test_module_base",
                           "test_xxx",
                           "test_yyy",
                           "test_zzz"],
                          sorted(module_names))

    def test_collect_test_cases(self):
        test_cases = self.loader.collect_test_cases()
        test_case_names = map(lambda case: case.__name__, test_cases)
        self.assert_equal(["TestXXX1",
                           "TestXXX2",
                           "TestYYY",
                           'test_module_base',
                           'test_xxx',
                           'test_yyy'],
                          sorted(test_case_names))

    def test_collect_test_cases_with_test_case_name_filter(self):
        self.loader.test_case_names = ["TestXXX1"]
        test_cases = self.loader.collect_test_cases()
        test_case_names = map(lambda case: case.__name__, test_cases)
        self.assert_equal(["TestXXX1"], sorted(test_case_names))

    def test_collect_test_cases_with_test_case_name_regexp_filter(self):
        self.loader.test_case_names = ["/XXX/"]
        test_cases = self.loader.collect_test_cases()
        test_case_names = map(lambda case: case.__name__, test_cases)
        self.assert_equal(["TestXXX1", "TestXXX2"], sorted(test_case_names))

    def test_create_test_suite(self):
        test_suite = self.loader.create_test_suite()
        self.assert_equal(
            ["test_module_base.test_top_level1",
             "test_module_base.test_top_level2",
             "test_xxx.TestXXX1.test_one",
             "test_xxx.TestXXX1.test_two",
             "test_yyy.TestYYY.test_xyz"],
            sorted(self._collect_test_names(test_suite)))

    def test_create_test_suite_with_test_name_filter(self):
        self.loader.test_names = ["test_one", "test_xyz"]
        test_suite = self.loader.create_test_suite()
        self.assert_equal(["test_xxx.TestXXX1.test_one",
                           "test_yyy.TestYYY.test_xyz"],
                          sorted(self._collect_test_names(test_suite)))

    def test_create_test_suite_with_test_name_regexp_filter(self):
        self.loader.test_names = ["/one|xyz/"]
        test_suite = self.loader.create_test_suite()
        self.assert_equal(["test_xxx.TestXXX1.test_one",
                           "test_yyy.TestYYY.test_xyz"],
                          sorted(self._collect_test_names(test_suite)))

    def test_create_test_suite_with_filters(self):
        self.loader.test_case_names = "TestXXX1"
        self.loader.test_names = ["test_one", "test_two"]
        test_suite = self.loader.create_test_suite()
        self.assert_equal(["test_xxx.TestXXX1.test_one",
                           "test_xxx.TestXXX1.test_two"],
                          sorted(self._collect_test_names(test_suite)))

    def test_create_test_suite_with_regexp_filters(self):
        self.loader.test_case_names = ["/XXX/", "/YYY/"]
        self.loader.test_names = ["/one|xyz/"]
        test_suite = self.loader.create_test_suite()
        self.assert_equal(["test_xxx.TestXXX1.test_one",
                           "test_yyy.TestYYY.test_xyz"],
                          sorted(self._collect_test_names(test_suite)))

    def _collect_test_names(self, test_suite):
        names = []
        for test_case_runner in test_suite._tests:
            names.extend([test.id() for test in test_case_runner.tests()])
        return names
