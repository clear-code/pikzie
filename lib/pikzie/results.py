from pikzie.color import *

def format_metadata(metadata, need_newline=False):
    if metadata is None or len(metadata) == 0:
        return ""
    formatted_metadata = map(lambda key: "  %s: %s" % (key, metadata[key]),
                             metadata)
    result = "\n".join(formatted_metadata)
    if need_newline:
        result += "\n"
    return result

class TestResult(object):
    pass

class Success(TestResult):
    name = "success"

    def __init__(self, test):
        self.fault = False
        self.critical = False
        self.symbol = "."
        self.test = test

    def detail(self):
        return ""

class Notification(TestResult):
    name = "notification"

    def __init__(self, test, message, traceback):
        self.fault = True
        self.critical = False
        self.symbol = "N"
        self.test = test
        self.message = message
        self.traceback = traceback

    def title(self):
        return "Notification: %s: %s" % (self.test, self.message)

    def detail(self):
        return ""

class Pending(TestResult):
    name = "pending"

    def __init__(self, test, message, traceback):
        self.fault = True
        self.critical = False
        self.symbol = "P"
        self.test = test
        self.message = message
        self.traceback = traceback

    def title(self):
        return "Pending: %s: %s" % (self.test, self.message)

    def detail(self):
        return ""

class Failure(TestResult):
    name = "failure"

    def __init__(self, test, message, traceback):
        self.fault = True
        self.critical = True
        self.symbol = "F"
        self.test = test
        self.message = message
        self.traceback = traceback

    def title(self):
        if len(self.traceback) == 0:
            return "Failure: %s" % self.test
        else:
            return "Failure: %s: %s" % (self.test, self.traceback[0].content)

    def detail(self):
        return self.message

class Error(TestResult):
    name = "error"

    def __init__(self, test, exception_type, message, traceback):
        self.fault = True
        self.critical = True
        self.symbol = "E"
        self.test = test
        self.exception_type = exception_type
        self.message = message
        self.traceback = traceback

    def title(self):
        return "Error: %s" % self.test

    def detail(self):
        return "%s: %s" % (self.exception_type, self.message)

FAULT_ORDER = [Notification, Pending, Failure, Error]

def compare_fault(fault1, fault2):
    return cmp(FAULT_ORDER.index(type(fault1)),
               FAULT_ORDER.index(type(fault2)))
