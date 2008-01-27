import sys
from optparse import OptionParser

import pikzie
from pikzie.core import *
from pikzie.ui.text import *

class Tester(object):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """
    def __init__(self):
        pass

    def run(self, argv=sys.argv):
        (options, args) = self._parse(argv)
        test = TestLoader().create_test_suite()
        runner = TextTestRunner()
        result = runner.run(test)
        if result.succeeded():
            return 0
        else:
            return 1

    def _parse(self, argv):
        parser = OptionParser(version=pikzie.version)
        parser.add_option("-n", "--name", metavar="TEST_NAME",
                          dest="test_name", help="Specify tests")
        parser.add_option("-t", "--test-case", metavar="TEST_CASE_NAME",
                          dest="test_case_name", help="Specify test cases")
        return parser.parse_args(argv[1:])
