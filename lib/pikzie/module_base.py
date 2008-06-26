import sys
from new import classobj

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
                raise TypeError, \
                      "did you mean: self.%s(%s)" % (assertion, inspected_args)
            return _assertion(__current_test_case__, *args, **kw_args)
        return run_assertion
    wrapped_assertion = wrap_assertion(assertion)
    assertions[assertion] = wrapped_assertion
    current_module.__dict__[assertion] = wrapped_assertion
    __all__.append(assertion)

def collect_test_case_from_module(self, module):
    test_cases = []
    pikzie_module = sys.modules.get("pikzie")
    if (pikzie_module is not None and
        pikzie_module in map(lambda name: getattr(module, name),
                             dir(module))):
        for assertion in assertions:
            if not module.__dict__.has_key(assertion):
                module.__dict__[assertion] = assertions[assertion]
        test_cases.append(classobj(module.__name__,
                                   (ModuleBasedTestCase,),
                                   {"target_module": module}))
    return test_cases

TestLoader.test_case_collectors.append(collect_test_case_from_module)

class ModuleBasedTestCase(TestCase):
    __current_test_case__ = None

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
