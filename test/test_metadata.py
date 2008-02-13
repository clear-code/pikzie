import pikzie

class TestMetadata(pikzie.TestCase):
    """Tests for test metadata."""

    class TestCase(pikzie.TestCase):
        def test_for_bug_111(self):
            pass
        test_for_bug_111 = pikzie.bug(111)(test_for_bug_111)

        def test_without_metadata(self):
            pass

    def test_bug(self):
        """Test for bug 111"""
        self.assert_metadata("bug", 111, "test_for_bug_111")

    def test_unknown_metadata(self):
        self.assert_metadata("unknown key", None, "test_without_metadata")

    def assert_metadata(self, name, expected_value, test_name):
        self.assert_equal(expected_value,
                          self.TestCase(test_name).get_metadata(name))
