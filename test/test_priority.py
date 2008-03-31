import pikzie
import test.utils

class TestPriority(pikzie.TestCase, test.utils.Assertions):
    """Tests for priority mode."""

    class TestCase(pikzie.TestCase):
        def test_must(self):
            pass
        test_must = pikzie.priority("must")(test_must)

        def test_important(self):
            pass
        test_important = pikzie.priority("important")(test_important)

        def test_high(self):
            pass
        test_high = pikzie.priority("high")(test_high)

        def test_normal(self):
            pass
        test_normal = pikzie.priority("normal")(test_normal)

        def test_low(self):
            pass
        test_low = pikzie.priority("low")(test_low)

        def test_never(self):
            pass
        test_never = pikzie.priority("never")(test_never)

    def test_priority(self):
        self.assert_need_to_run_according_to_priority("test_must", 1.0, 0.0001)
        self.assert_need_to_run_according_to_priority("test_important",
                                                      0.9, 0.09)
        self.assert_need_to_run_according_to_priority("test_high", 0.70, 0.1)
        self.assert_need_to_run_according_to_priority("test_normal", 0.5, 0.1)
        self.assert_need_to_run_according_to_priority("test_low", 0.25, 0.1)
        self.assert_need_to_run_according_to_priority("test_never", 0.0, 0.0001)

    def assert_need_to_run_according_to_priority(self, test_name,
                                                 expected, delta):
        n = 1000
        n_need_to_run = 0
        for i in range(0, n):
            if self.TestCase(test_name)._need_to_run_according_to_priority():
                n_need_to_run +=1
        self.assert_in_delta(expected, float(n_need_to_run) / n, delta)
