import sys
from new import classobj

from pikzie.core import *
from pikzie.assertions import Assertions

__all__ = []

def _collect_test_case_from_module(self, module):
    test_cases = []
    pikzie_module = sys.modules["pikzie"]
    if (pikzie_module is not None and
        pikzie_module in map(lambda name: getattr(module, name),
                             dir(module))):
        test_cases.append(classobj(module.__name__,
                                   (ModuleBasedTestCase,),
                                   {"target_module": module}))
    return test_cases

TestLoader.test_case_collectors.append(_collect_test_case_from_module)

class ModuleBasedTestCase(TestCase):
    def collect_test(cls):
        def _is_test_method(name):
            object = getattr(cls.target_module, name)
            return (hasattr(object, "func_code") and
                    object.func_code.co_argcount == 0)
        return map(cls, filter(_is_test_method, dir(cls.target_module)))
    collect_test = classmethod(collect_test)

    def __init__(self, method_name):
        TestCase.__init__(self, method_name)

    def _test_method(self):
        return getattr(self.__class__.target_module, self._method_name())

    def _test_case_name(self):
        return self.__class__.target_module.__name__

    def __str__(self):
        return self.id()

    def __repr__(self):
        return "<%s method_name=%s description=%s>" % \
               (str(self.__class__.target_module),
                self._method_name(), self.__description)

    def setup(self):
        setup = getattr(self.__class__.target_module, "setup", None)
        if setup:
            setup()

    def teardown(self):
        teardown = getattr(self.__class__.target_module, "teardown", None)
        if teardown:
            teardown()

