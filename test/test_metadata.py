import pikzie
import test.utils

class TestMetadata(pikzie.TestCase, test.utils.Assertions):
    """Tests for test metadata."""

    class TestCase(pikzie.TestCase):
        def test_for_bug_111(self):
            self.fail("This is a bug!!!")
        test_for_bug_111 = pikzie.bug(111)(test_for_bug_111)

        def test_without_metadata(self):
            self.assert_equal(1, 1)

        def test_with_metadata(self):
            self.assert_equal(1, 1)
        test_with_metadata = pikzie.metadata("key", "value")(test_with_metadata)


    def test_bug(self):
        """Test for bug 111"""
        self.assert_metadata("bug", 111, "test_for_bug_111")

    def test_bug_result(self):
        self.assert_result(False, 1, 0, 1, 0, 0, 0, 0,
                           [("F",
                             "TestCase.test_for_bug_111",
                             "This is a bug!!!",
                             {"bug": 111})],
                           ["test_for_bug_111"])

    def test_unknown_metadata_for_test_without_metadata(self):
        self.assert_metadata("unknown key", None, "test_without_metadata")

    def test_unknown_metadata_for_test_with_metadata(self):
        self.assert_metadata("key", "value", "test_with_metadata")
        self.assert_metadata("unknown key", None, "test_with_metadata")

    def assert_metadata(self, name, expected_value, test_name):
        self.assert_equal(expected_value,
                          self.TestCase(test_name).get_metadata(name))
