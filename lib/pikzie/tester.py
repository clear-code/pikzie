import sys
import atexit
from optparse import OptionParser

from pikzie.core import *
from pikzie.ui.console import *

class Tester(object):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """

    ran = False

    def __init__(self, version=None, target_modules=None):
        self.version = version
        if target_modules is not None:
            def ensure_module(module_or_name):
                if type(module_or_name) == str:
                    return sys.modules[module_or_name]
                else:
                    return module_or_name
            target_modules = map(ensure_module, target_modules)
        self.target_modules = target_modules

    def run(self, args=None):
        self.__class__.ran = True
        options, args = self._parse(args)
        options = options.__dict__
        test_suite_create_options = {
            "pattern": options.pop("test_file_name_pattern"),
            "test_name": options.pop("test_name"),
            "test_case_name": options.pop("test_case_name"),
            "target_modules": self.target_modules
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

def auto_test_run():
    if not Tester.ran:
        sys.exit(Tester(target_modules=['__main__']).run())

atexit.register(auto_test_run)
