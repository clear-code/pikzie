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

class Notification(object):
    name = "notification"

    def __init__(self, test, detail, traceback):
        self.critical = False
        self.single_character_display = "N"
        self.test = test
        self.detail = detail
        self.traceback = traceback

    def long_display(self):
        result = "Notification: %s: %s" % (self.test, self.detail)
        metadata = format_metadata(self.test.metadata)
        if metadata:
            result += "\n" + metadata
        return result

class Pending(object):
    name = "pending"

    def __init__(self, test, detail, traceback):
        self.critical = False
        self.single_character_display = "P"
        self.test = test
        self.detail = detail
        self.traceback = traceback

    def long_display(self):
        result = "Pending: %s: %s" % (self.test, self.detail)
        metadata = format_metadata(self.test.metadata)
        if metadata:
            result += "\n" + metadata
        return result

class Failure(object):
    name = "failure"

    def __init__(self, test, detail, traceback):
        self.critical = True
        self.single_character_display = "F"
        self.test = test
        self.detail = detail
        self.traceback = traceback

    def long_display(self):
        metadata = format_metadata(self.test.metadata, True)
        if len(self.traceback) == 0:
            return "Failure: %s\n%s%s" % (self.test, metadata, self.detail)
        else:
            return "Failure: %s: %s\n%s%s" % \
                (self.test, self.traceback[0].content, metadata, self.detail)

class Error(object):
    name = "error"

    def __init__(self, test, exception_type, detail, traceback):
        self.critical = True
        self.single_character_display = "E"
        self.test = test
        self.exception_type = exception_type
        self.detail = detail
        self.traceback = traceback

    def long_display(self):
        return "Error: %s\n%s%s: %s" % \
            (self.test, format_metadata(self.test.metadata, True),
             self.exception_type, self.detail)

FAULT_ORDER = [Notification, Pending, Failure, Error]

def compare_fault(fault1, fault2):
    return cmp(FAULT_ORDER.index(type(fault1)),
               FAULT_ORDER.index(type(fault2)))
