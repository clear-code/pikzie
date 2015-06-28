# Copyright (C) 2009-2015  Kouhei Sutou <kou@clear-code.com>
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

from pikzie.color import *

def format_metadata(metadata, need_newline=False):
    if metadata is None:
        return ""
    format_keys = filter(lambda key: key != "data", metadata)
    formatted_metadata = ["  %s: %s" % (key, metadata[key])
                          for key
                          in sorted(format_keys)]
    if len(formatted_metadata) == 0:
        return ""
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
        self.traceback = None

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

class Omission(TestResult):
    name = "omission"

    def __init__(self, test, message, traceback):
        self.fault = True
        self.critical = False
        self.symbol = "O"
        self.test = test
        self.message = message
        self.traceback = traceback

    def title(self):
        return "Omission: %s: %s" % (self.test, self.message)

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

    def __init__(self, test, message, traceback, expected=None, actual=None):
        self.fault = True
        self.critical = True
        self.symbol = "F"
        self.test = test
        self.message = message
        self.traceback = traceback
        self.expected = expected
        self.actual = actual

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

FAULT_ORDER = [Notification, Omission, Pending, Failure, Error]

def fault_compare_key(fault):
    return FAULT_ORDER.index(type(fault))
