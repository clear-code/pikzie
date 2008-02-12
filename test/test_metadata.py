import pikzie

class TestMetadata(pikzie.TestCase):
    """Tests for metadata of TestCase."""

    class TestCase(pikzie.TestCase):
        def test_for_bug_111(self):
            self.fail("Failed!!!")
        test_for_bug_111 = pikzie.bug(111)(test_for_bug_111)

    def test_bug(self):
        """Test for bug 111"""
        self.assert_metadata("bug", 111, "test_for_bug_111")

    def assert_metadata(self, name, expected_value, test_name):
        self.assert_equal(expected_value,
                          self.TestCase(test_name).get_metadata(name))
