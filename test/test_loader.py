import pikzie

class TestLoader(pikzie.TestCase):
    def setup(self):
        self.fixture_dir = "test/fixtures/tests"
        pattern = self.fixture_dir + "/test_*.py"
        self.loader = pikzie.TestLoader(pattern)

    def test_find_targets(self):
        def build_full_path(name):
            return "%s/test_%s.py" % (self.fixture_dir, name)

        self.assert_equal(sorted(map(build_full_path, ["xxx", "yyy", "zzz"])),
                          sorted(self.loader._find_targets()))

    def test_load_modules(self):
        modules = self.loader._load_modules()
        module_names = map(lambda module: module.__name__, modules)
        self.assert_equal(["test.fixtures.tests.test_xxx",
                           "test.fixtures.tests.test_yyy",
                           "test.fixtures.tests.test_zzz"],
                          sorted(module_names))

    def test_collect_test_cases(self):
        test_cases = self.loader.collect_test_cases()
        test_case_names = map(lambda case: case.__name__, test_cases)
        self.assert_equal(["TestXXX1", "TestXXX2", "TestYYY"],
                          sorted(test_case_names))

    def test_collect_test_cases_with_test_case_name_filter(self):
        self.loader.test_case_name = "XXX"
        test_cases = self.loader.collect_test_cases()
        test_case_names = map(lambda case: case.__name__, test_cases)
        self.assert_equal(["TestXXX1", "TestXXX2"],
                          sorted(test_case_names))

    def test_create_test_suite(self):
        test_suite = self.loader.create_test_suite()
        test_names = map(lambda test: test.id(), test_suite._tests)
        self.assert_equal(["test.fixtures.tests.test_xxx.TestXXX1.test_one",
                           "test.fixtures.tests.test_xxx.TestXXX1.test_two",
                           "test.fixtures.tests.test_yyy.TestYYY.test_xyz"],
                          sorted(test_names))

    def test_create_test_suite_with_test_name_filter(self):
        self.loader.test_name = "one|xyz"
        test_suite = self.loader.create_test_suite()
        test_names = map(lambda test: test.id(), test_suite._tests)
        self.assert_equal(["test.fixtures.tests.test_xxx.TestXXX1.test_one",
                           "test.fixtures.tests.test_yyy.TestYYY.test_xyz"],
                          sorted(test_names))
