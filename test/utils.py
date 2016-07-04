import sys
import re
import pikzie

import pikzie.pretty_print as pp

def collect_fault_info(fault):
    if hasattr(fault, "expected") and fault.expected and fault.actual:
        message = \
            ("expected: <%s>\n but was: <%s>") % \
            (fault.expected, fault.actual)
        if fault.message:
            message = fault.message + "\n" + message
    else:
        message = fault.message
    return (fault.symbol,
            str(fault.test),
            str(message),
            fault.test.metadata)

class Assertions(object):
    class RegexpMatchResult(object):
        def __init__(self, succeeded, test_result, fault_infos):
            self.succeeded = succeeded
            self.test_result = test_result
            self.fault_infos = list(fault_infos)

        def __eq__(self, other):
            if self.succeeded != other.succeeded: return False
            if self.test_result != other.test_result: return False
            if self.fault_infos == other.fault_infos: return True
            if len(self.fault_infos) != len(other.fault_infos): return False
            i = 0
            for fault_info in self.fault_infos:
                other_fault_info = other.fault_infos[i]
                if not self._regexp_support_string_equal(fault_info[0],
                                                         other_fault_info[0]):
                    return False
                if not self._regexp_support_string_equal(fault_info[1],
                                                         other_fault_info[1]):
                    return False
                if not self._regexp_support_string_equal(fault_info[2],
                                                         other_fault_info[2]):
                    return False
            return True

        def __repr__(self):
            def extract_pattern(pattern_or_string):
                if hasattr(pattern_or_string, "pattern"):
                    return pattern_or_string.pattern
                else:
                    return pattern_or_string
            patterns = [[extract_pattern(pattern_or_string)
                         for pattern_or_string
                         in fault_info]
                        for fault_info
                        in self.fault_infos]
            return str((self.succeeded, self.test_result, patterns))

        _pattern_class = type(re.compile(""))
        def _regexp_support_string_equal(self, value1, value2):
            if value1 == value2: return True
            if isinstance(value1, str) and isinstance(value2, str): return False
            if isinstance(value1, self._pattern_class):
                return re.search(value1, value2) is not None
            if isinstance(value2, self._pattern_class):
                return re.search(value2, value1) is not None
            return False

    def assert_result(self, succeeded, n_tests, n_assertions, n_failures,
                      n_errors, n_pendings, n_omissions, n_notifications,
                      fault_info, tests):
        context = pikzie.TestRunnerContext()
        for test_name in tests:
            self.TestCase(test_name).run(context)

            if context.need_interrupt():
                raise KeyboardInterrupt

        self.assert_equal(self.RegexpMatchResult(succeeded,
                                                 (n_tests,
                                                  n_assertions,
                                                  n_failures,
                                                  n_errors,
                                                  n_pendings,
                                                  n_omissions,
                                                  n_notifications),
                                                 fault_info),
                          self.RegexpMatchResult(context.succeeded,
                                                 (context.n_tests,
                                                  context.n_assertions,
                                                  context.n_failures,
                                                  context.n_errors,
                                                  context.n_pendings,
                                                  context.n_omissions,
                                                  context.n_notifications),
                                                 map(collect_fault_info,
                                                     context.faults)))

    def assert_success_output(self, n_tests, n_assertions, tests):
        self.assert_output("." * n_tests, n_tests, n_assertions, 0, 0, 0, 0, 0,
                           "", tests)

    def assert_output(self, progress, n_tests, n_assertions, n_failures,
                      n_errors, n_pendings, n_omissions, n_notifications,
                      details, tests):
        suite = pikzie.TestSuite(tests)
        context = self.runner.run(suite)
        self.assert_equal((n_tests, n_assertions, n_failures, n_errors,
                           n_pendings, n_omissions, n_notifications),
                          (context.n_tests, context.n_assertions,
                           context.n_failures, context.n_errors,
                           context.n_pendings, context.n_omissions,
                           context.n_notifications))
        self.output.seek(0)
        message = self.output.read()
        format = \
            "%s\n" \
            "%s" \
            "Finished in %.3f seconds\n" \
            "\n" \
            "%d test(s), %d assertion(s), %d failure(s), %d error(s), " \
            "%d pending(s), %d omission(s), %d notification(s)\n"
        self.assert_equal(format % (progress, details, context.elapsed,
                                    n_tests, n_assertions, n_failures,
                                    n_errors, n_pendings, n_omissions,
                                    n_notifications),
                          message)

class Source(object):
    def current_file(self):
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            return sys.exc_info()[2].tb_frame.f_back.f_code.co_filename
    current_file = classmethod(current_file)

    def current_line_no(self):
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            return sys.exc_info()[2].tb_frame.f_back.f_lineno
    current_line_no = classmethod(current_line_no)

    def find_target_line_no(self, pattern, file_name=None):
        if file_name is None:
            try:
                raise ZeroDivisionError
            except ZeroDivisionError:
                frame = sys.exc_info()[2].tb_frame.f_back
                file_name = frame.f_code.co_filename
        line_no = -1
        if type(pattern) == type(""):
            pattern = re.compile(re.escape(pattern))
        try:
            f = open(file_name)
            for i, line in enumerate(f):
                if pattern.search(line):
                    line_no = i + 1
                    break
        finally:
            f.close()
        return line_no
    find_target_line_no = classmethod(find_target_line_no)
