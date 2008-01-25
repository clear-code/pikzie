import sys
import re
import pprint
import difflib

class Assertions(object):
    def fail(self, message):
        self._fail(message)

    def assert_none(self, expression, message=None):
        if expression is None:
            self._pass_assertion()
        else:
            system_message = "expected: <%r> is None" % expression
            self._fail(system_message, message)

    def assert_not_none(self, expression, message=None):
        if expression is not None:
            self._pass_assertion()
        else:
            self._fail("expected: not None", message)

    def assert_true(self, expression, message=None):
        if expression:
            self._pass_assertion()
        else:
            system_message = "expected: <%r> is a true value" % expression
            self._fail(system_message, message)

    def assert_false(self, expression, message=None):
        if expression:
            system_message = "expected: <%r> is a false value" % expression
            self._fail(system_message, message)
        else:
            self._pass_assertion()

    def assert_equal(self, expected, actual, message=None):
        if expected == actual:
            self._pass_assertion()
        else:
            expected = pprint.pformat(expected)
            actual = pprint.pformat(actual)
            diff = difflib.ndiff(expected.splitlines(), actual.splitlines())
            system_message = "expected: <%s>\n but was: <%s>\ndiff:\n%s" % \
                (expected, actual, "\n".join(diff))
            self._fail(system_message, message)

    def assert_not_equal(self, not_expected, actual, message=None):
        if not_expected != actual:
            self._pass_assertion()
        else:
            not_expected = pprint.pformat(not_expected)
            actual = pprint.pformat(actual)
            system_message = "not expected: <%s>\n     but was: <%s>" % \
                (not_expected, actual)
            if not_expected != actual:
                diff = difflib.ndiff(not_expected.splitlines(),
                                     actual.splitlines())
                system_message = "%s\ndiff:\n%s" % \
                    (system_message, "\n".join(diff))
            self._fail(system_message, message)

    def assert_in_delta(self, expected, actual, delta, message=None):
        lower = expected - delta
        upper = expected + delta
        if lower <= actual <= upper:
            self._pass_assertion()
        else:
            expected = pprint.pformat(expected)
            actual = pprint.pformat(actual)
            delta = pprint.pformat(delta)
            range = pprint.pformat([lower, upper])
            system_message = "expected: <%s+-%s %s>\n but was: <%s>" % \
                (expected, delta, range, actual)
            self._fail(system_message, message)

    def assert_match(self, pattern, target, message=None):
        if re.match(pattern, target):
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.match(%s, %s) is not None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_not_match(self, pattern, target, message=None):
        if re.match(pattern, target) is None:
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.match(%s, %s) is None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_search(self, pattern, target, message=None):
        if re.search(pattern, target):
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.search(%s, %s) is not None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_not_found(self, pattern, target, message=None):
        if re.search(pattern, target) is None:
            self._pass_assertion()
        else:
            pattern_repr = self._pformat_re_repr(pattern)
            pattern = self._pformat_re(pattern)
            target = pprint.pformat(target)
            format = \
                "expected: re.search(%s, %s) is None\n" \
                " pattern: <%s>\n" \
                "  target: <%s>"
            system_message = format % (pattern_repr, target, pattern, target)
            self._fail(system_message, message)

    def assert_hasattr(self, object, name, message=None):
        if hasattr(object, name):
            self._pass_assertion()
        else:
            object = pprint.pformat(object)
            name = pprint.pformat(name)
            system_message = "expected: hasattr(%s, %s)" % (object, name)
            self._fail(system_message, message)

    def assert_callable(self, object, message=None):
        if callable(object):
            self._pass_assertion()
        else:
            object = pprint.pformat(object)
            system_message = "expected: callable(%s)" % (object)
            self._fail(system_message, message)

    def assert_call_raise(self, exception, callable_object, *args, **kw_args):
        try:
            callable_object(*args, **kw_args)
        except exception:
            self._pass_assertion()
        except:
            actual = sys.exc_info()
            actual_exception_class, actual_exception_value = actual[:2]
            message = \
                "expected: <%s> is raised\n" \
                " but was: <%s>(%s)" % \
                (self._pformat_exception_class(exception),
                 self._pformat_exception_class(actual_exception_class),
                 str(actual_exception_value))
            self._fail(message)
        else:
            message = \
                "expected: <%s> is raised\n" \
                " but was: nothing raised" % \
                self._pformat_exception_class(exception)
            self._fail(message)

