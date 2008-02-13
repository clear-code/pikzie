from pikzie.color import *

def format_metadata(metadata):
    if metadata is None or len(metadata) == 0:
        return ""
    formatted_metadata = map(lambda key: "  %s: %s" % (key, metadata[key]),
                             metadata)
    return "\n".join(formatted_metadata) + "\n"

class Pending(object):
    def __init__(self, test, detail, tracebacks):
        self.critical = False
        self.single_character_display = "P"
        self.color = COLORS["yellow"]
        self.test = test
        self.detail = detail
        self.tracebacks = tracebacks

    def long_display(self):
        metadata = format_metadata(self.test.metadata)
        return "Pending: %s: %s\n%s%s" % \
            (self.test, self.detail, metadata,
             "\n".join(map(str, self.tracebacks)))

class Failure(object):
    def __init__(self, test, detail, tracebacks):
        self.critical = True
        self.single_character_display = "F"
        self.color = COLORS["red"]
        self.test = test
        self.detail = detail
        self.tracebacks = tracebacks

    def long_display(self):
        metadata = format_metadata(self.test.metadata)
        if len(self.tracebacks) == 0:
            return "Failure: %s\n%s%s" % (self.test, metadata, self.detail)
        else:
            return "Failure: %s: %s\n%s%s\n%s" % \
                (self.test, self.tracebacks[0].line, metadata,
                 self.detail, "\n".join(map(str, self.tracebacks)))

class Error(object):
    def __init__(self, test, exception_type, detail, tracebacks):
        self.critical = True
        self.single_character_display = "E"
        self.color = COLORS["purple"]
        self.test = test
        self.exception_type = exception_type
        self.detail = detail
        self.tracebacks = tracebacks

    def long_display(self):
        return "Error: %s\n%s%s: %s\n%s" % \
            (self.test, self.exception_type,
             format_metadata(self.test.metadata),
             self.detail, "\n".join(map(str, self.tracebacks)))

FAULT_ORDER = [Pending, Failure, Error]

def compare_fault(fault1, fault2):
    return cmp(FAULT_ORDER.index(type(fault1)),
               FAULT_ORDER.index(type(fault2)))
