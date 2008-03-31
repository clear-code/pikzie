import pikzie

class TestXXX1(pikzie.TestCase):
    default_priority = "must"
    def no_test(self):
        pass

    def test_one(self):
        pass

    def test_two(self):
        pass

class TestXXX2(pikzie.TestCase):
    default_priority = "must"
    pass
