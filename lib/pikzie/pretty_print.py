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

import re
import types
import difflib
import pprint

def format(object):
    return pprint.pformat(object)

_re_class = type(re.compile(""))
def _re_flags(pattern):
    result = ""
    if isinstance(pattern, _re_class):
        if pattern.flags & re.IGNORECASE: result += "i"
        if pattern.flags & re.LOCALE: result += "l"
        if pattern.flags & re.MULTILINE: result += "m"
        if pattern.flags & re.DOTALL: result += "s"
        if pattern.flags & re.UNICODE: result += "u"
        if pattern.flags & re.VERBOSE: result += "x"
    return result

def _re_flags_repr(pattern):
    flags = []
    if isinstance(pattern, _re_class):
        if pattern.flags & re.IGNORECASE: flags.append("re.IGNORECASE")
        if pattern.flags & re.LOCALE: flags.append("re.LOCALE")
        if pattern.flags & re.MULTILINE: flags.append("re.MULTILINE")
        if pattern.flags & re.DOTALL: flags.append("re.DOTALL")
        if pattern.flags & re.UNICODE: flags.append("re.UNICODE")
        if pattern.flags & re.VERBOSE: flags.append("re.VERBOSE")
    if len(flags) == 0:
        return None
    else:
        return " | ".join(flags)

def format_re(pattern):
    re_flags = _re_flags(pattern)
    if hasattr(pattern, "pattern"):
        pattern = pattern.pattern
    pattern = format(pattern)
    return "/%s/%s" % (pattern[1:-1], re_flags)

def format_re_repr(pattern):
    re_flags_repr = _re_flags_repr(pattern)
    if hasattr(pattern, "pattern"):
        pattern = pattern.pattern
    pattern = pprint.pformat(pattern)
    if re_flags_repr:
        return "re.compile(%s, %s)" % (pattern, re_flags_repr)
    else:
        return pattern

def format_callable_object(callable_object):
    if hasattr(callable_object, "im_class"):
        cls = callable_object.im_class
        return "%s.%s.%s" % (cls.__module__,
                             cls.__class__.__name__,
                             callable_object.__name__)
    else:
        return "%s.%s" % (callable_object.__module__,
                          callable_object.__name__)

def format_call_arguments(args, kw_args):
    formatted_args = [format(arg) for arg in args]
    formatted_args.extend(["%s=%s" % (format(key), format(value))
                           for (key, value) in kw_args.items()])
    return ", ".join(formatted_args)

def format_call(callable_object, args, kw_args):
    return "%s(%s)" % (format_callable_object(callable_object),
                       format_call_arguments(args, kw_args))

def format_exception_class(exception_class):
    if issubclass(exception_class, Exception) or \
            issubclass(exception_class, types.ClassType):
        return str(exception_class)
    else:
        return format(exception_class)

def format_for_diff(object):
    if not isinstance(object, str):
        object = format(object)
    return object

def format_diff(string1, string2):
    def ensure_newline(string):
        if string.endswith("\n"):
            return string
        else:
            return string + "\n"
    diff = difflib.ndiff(ensure_newline(string1).splitlines(True),
                         ensure_newline(string2).splitlines(True))
    return "".join(diff).rstrip()

def is_interested_diff(diff):
    if not diff:
        return False
    if not re.search("^[-+]", diff, re.MULTILINE):
        return False
    if re.search("^[ ?]", diff, re.MULTILINE):
        return True
    if re.search("(?:.*\n){2,}", diff):
        return True
    return False

def need_fold(diff):
    return re.search("^[-?+].{79}", diff, re.MULTILINE)

def fold(string):
    def fold_line(line):
        return re.subn("(.{78})", "\\1\n", line)[0]
    return "\n".join([fold_line(line) for line in string.split("\n")])

def format_folded_diff(string1, string2):
    return format_diff(fold(string1), fold(string2))

def append_diff(message, target1, target2):
    formatted_target1 = format_for_diff(target1)
    formatted_target2 = format_for_diff(target2)
    diff = format_diff(formatted_target1, formatted_target2)
    if is_interested_diff(diff):
        message = "%s\n\ndiff:\n%s" % (message, diff)
    if need_fold(diff):
        folded_diff = format_folded_diff(formatted_target1, formatted_target2)
        message = "%s\n\nfolded diff:\n%s" % (message, folded_diff)
    return message

