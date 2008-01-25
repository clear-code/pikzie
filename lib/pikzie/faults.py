from color import *

class Fault(Exception):
    def __init__(self, message, user_message=None):
        self.message = message
        self.user_message = user_message

    def __str__(self):
        result = self.message
        if self.user_message:
            result += self.user_message + "\n"
        return result

class Failure(object):
    def __init__(self, test, detail, tracebacks):
        self.test = test
        self.detail = detail
        self.tracebacks = tracebacks

    def single_character_display(self):
        return "F"

    def color(self):
        return COLORS["red"]

    def long_display(self):
        if len(self.tracebacks) == 0:
            return "Failure: %s\n%s" % (self.test, self.detail)
        else:
            return "Failure: %s: %s\n%s\n%s" % \
                (self.test, self.tracebacks[0].line,
                 self.detail, "\n".join(map(str, self.tracebacks)))

class Error(object):
    def __init__(self, test, exception_type, detail, tracebacks):
        self.test = test
        self.exception_type = exception_type
        self.detail = detail
        self.tracebacks = tracebacks

    def single_character_display(self):
        return "E"

    def color(self):
        return COLORS["purple"]

    def long_display(self):
        return "Error: %s\n%s: %s\n%s" % \
            (self.test, self.exception_type,
             self.detail, "\n".join(map(str, self.tracebacks)))

FAULT_RANK = {
    Failure: 0,
    Error: 1,
}

def compare_fault(fault1, fault2):
    return cmp(FAULT_RANK[type(fault1)], FAULT_RANK[type(fault2)])
