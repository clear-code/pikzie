import pikzie

def test_assert_equal_success():
    assert_equal(1, 1)
    assert_equal("abc", "abc")

def test_assert_equal_fail():
    assert_equal(2, 1)
