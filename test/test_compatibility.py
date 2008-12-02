import time
import pikzie

class TestCompatibility(pikzie.TestCase):
    """Tests for version compatibility"""

    def test_strptime(self):
        self.assert_equal((2008, 11, 10, 0, 0, 0, 0, 315, -1),
                          time.strptime('2008 Nov 10 00:00:00',
                                        '%Y %b %d %H:%M:%S'))
