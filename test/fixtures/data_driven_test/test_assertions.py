import pikzie

def test_assert_equal(data):
    assert_equal(data["expected"], data["actual"])
test_assert_equal = \
    pikzie.data("success",
                {"expected": "abc", "actual": "abc"})(test_assert_equal)
test_assert_equal = \
    pikzie.data("fail",
                {"expected": "abc", "actual": "def"})(test_assert_equal)
test_assert_equal = \
    pikzie.data("another-success",
                {"expected": "def", "actual": "def"})(test_assert_equal)
