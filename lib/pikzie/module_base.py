# Copyright (C) 2009-2011  Kouhei Sutou <kou@clear-code.com>
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

from pikzie.core import *
from pikzie.assertions import Assertions

__all__ = []

__current_test_case__ = None
current_module = sys.modules[__name__]
assertions = {}
for assertion in filter(lambda name: not name.startswith("_"), dir(Assertions)):
    def wrap_assertion(assertion):
        _assertion = getattr(Assertions, assertion)
        def run_assertion(*args, **kw_args):
            if __current_test_case__ is None:
                def inspect_kw_arg(arg):
                    return arg + ("=%s" % kw_args[arg])
                inspected_args = ", ".join(map(str, args) +
                                           map(inspect_kw_arg, kw_args))
                raise TypeError("did you mean: self.%s(%s)" % \
                                    (assertion, inspected_args))
            return _assertion(__current_test_case__, *args, **kw_args)
        return run_assertion
    wrapped_assertion = wrap_assertion(assertion)
    assertions[assertion] = wrapped_assertion
    current_module.__dict__[assertion] = wrapped_assertion
    __all__.append(assertion)

def collect_test_case_from_module(self, module):
    test_cases = []
    pikzie_module = sys.modules.get("pikzie")
    if (pikzie_module is None):
        return []
    module_object = type(pikzie_module)
    def _is_module(_object):
        return type(_object) == module_object
    if (pikzie_module in filter(_is_module,
                                map(lambda name: getattr(module, name),
                                    dir(module)))):
        for assertion in assertions:
            if not assertion in module.__dict__:
                module.__dict__[assertion] = assertions[assertion]
        test_cases.append(type(module.__name__,
                               (ModuleBasedTestCase,),
                               {"target_module": module}))
    return test_cases

TestLoader.test_case_collectors.append(collect_test_case_from_module)

class ModuleBasedTestCase(TestCase):
    __current_test_case__ = None

    def collect_test(cls):
        return cls._collect_test(cls.target_module, 0)
    collect_test = classmethod(collect_test)

    def _test_method(self):
        return getattr(self.__class__.target_module, self._method_name())

    def _test_case_name(self):
        return self.__class__.target_module.__name__

    def __str__(self):
        return self.id()

    def __repr__(self):
        return "<%s method_name=%s description=%s data_label=%s data=%s>" % \
            (str(self.__class__.target_module),
             self._method_name(), self.__description,
             self.__data_label, str(self.__data))

    def _run_setup(self, context):
        setup = getattr(self.__class__.target_module, "setup", None)
        if setup:
            setup()

    def _run_teardown(self, context):
        teardown = getattr(self.__class__.target_module, "teardown", None)
        if teardown:
            teardown()

    def _run_test(self, context):
        global __current_test_case__
        before_test_case = __current_test_case__
        try:
            __current_test_case__ = self
            return TestCase._run_test(self, context)
        finally:
            __current_test_case__ = before_test_case
