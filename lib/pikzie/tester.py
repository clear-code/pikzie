import sys

from pikzie.core import *
from pikzie.ui.text import *

class Tester(object):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """
    def __init__(self):
        pass

    def run(self, argv=sys.argv):
#         if not self._parse(argv):
#             return 2
        test = TestLoader().create_test_suite()
        runner = TextTestRunner()
        result = runner.run(test)
        if result.succeeded():
            return 0
        else:
            return 1
