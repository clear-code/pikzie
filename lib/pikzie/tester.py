import sys
from optparse import OptionParser

from pikzie.core import *
from pikzie.ui.console import *

class Tester(object):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """
    def __init__(self, version=None):
        self.version = version

    def run(self, args=None):
        options, args = self._parse(args)
        options = options.__dict__
        test_suite_create_options = {
            "pattern": options.pop("test_file_name_pattern"),
            "test_name": options.pop("test_name"),
            "test_case_name": options.pop("test_case_name")
        }
        test = TestLoader(**test_suite_create_options).create_test_suite(args)
        runner = ConsoleTestRunner(**options)
        result = runner.run(test)
        if result.succeeded():
            return 0
        else:
            return 1

    def _parse(self, args):
        parser = OptionParser(version=self.version,
                              usage="%prog [options] [test_files]")
        group = parser.add_option_group("Common", "Common options")
        group.add_option("-p", "--test-file-name-pattern",
                         metavar="PATTERN", dest="test_file_name_pattern",
                         help="Glob for test file name "
                         "(default: %s)" % TestLoader.default_pattern)
        group.add_option("-n", "--name", metavar="TEST_NAME",
                         dest="test_name", help="Specify tests")
        group.add_option("-t", "--test-case", metavar="TEST_CASE_NAME",
                         dest="test_case_name", help="Specify test cases")
        ConsoleTestRunner.setup_options(parser)
        return parser.parse_args(args)
