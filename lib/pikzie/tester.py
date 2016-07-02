# Copyright (C) 2009  Kouhei Sutou <kou@clear-code.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import atexit
from optparse import OptionParser

from pikzie.core import *
from pikzie.ui.console import *
import pikzie.report

class Tester(object):
    """
    A command-line program that runs a set of tests; this is primarily
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
            target_modules = list(map(ensure_module, target_modules))
        self.target_modules = target_modules

    def run(self, args=None):
        self.__class__.ran = True
        options, args = self._parse(args)
        options = options.__dict__
        test_suite_create_options = {
            "base_dir": options.pop("base_dir"),
            "ignore_dirs": options.pop("ignore_dirs"),
            "pattern": options.pop("test_file_name_pattern"),
            "test_names": options.pop("test_names"),
            "test_case_names": options.pop("test_case_names"),
            "target_modules": self.target_modules,
            "priority_mode": options.pop("priority_mode")
        }
        xml_report = options.pop("xml_report")
        test = TestLoader(**test_suite_create_options).create_test_suite(args)
        runner = ConsoleTestRunner(**options)
        listeners = []
        if xml_report:
            listeners.append(pikzie.report.XML(xml_report))
        context = runner.run(test, listeners)
        if context.succeeded:
            return 0
        else:
            return 1

    def _parse(self, args):
        parser = OptionParser(version=self.version,
                              usage="%prog [options] [test_files]")
        group = parser.add_option_group("Common", "Common options")
        group.add_option("--base-dir",
                         metavar="DIR", dest="base_dir",
                         help="Base directory that has tests "
                         "(default: %s)" % TestLoader.default_base_dir)
        group.add_option("--ignore-directory", metavar="DIRECTORY",
                         action="append", dest="ignore_dirs",
                         help="Don't load tests under DIRECTORY "
                         "(default: %r)" % TestLoader.default_ignore_dirs)
        group.add_option("-p", "--test-file-name-pattern",
                         metavar="PATTERN", dest="test_file_name_pattern",
                         help="Glob for test file base name "
                         "(default: %s)" % TestLoader.default_pattern)
        group.add_option("-n", "--name", metavar="TEST_NAME",
                         action="append", dest="test_names",
                         help="Specify tests")
        group.add_option("-t", "--test-case", metavar="TEST_CASE_NAME",
                         action="append", dest="test_case_names",
                         help="Specify test cases")
        group.add_option("--xml-report", metavar="FILE",
                         dest="xml_report",
                         help="Report test result to FILE as XML")
        group.add_option("--priority", action="store_true", default=False,
                         dest="priority_mode", help="Use priority mode")
        group.add_option("--no-priority", action="store_false",
                         dest="priority_mode", help="Not use priority mode")
        ConsoleTestRunner.setup_options(parser)
        return parser.parse_args(args)

auto_test_run_reject_pattern = \
    r"\b(?:pydoc[\d.]*|setup\.py|ipython[\d.]*|easy_install[\d.]*)$"

def auto_test_run():
    if Tester.ran: return
    if not sys.argv[0]: return
    if sys.argv[0] == '-c': return
    if re.search(auto_test_run_reject_pattern, sys.argv[0]): return
    sys.exit(Tester(target_modules=['__main__']).run())

atexit.register(auto_test_run)
