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

import cgi

class XML(object):
    def __init__(self, output):
        self.file = isinstance(output, str)
        if self.file:
            output = open(output, "w")
        self.output = output
        self.have_test = False

    def on_start_test(self, report, test):
        if not self.have_test:
            self.have_test = True
            self._write("<report>\n")

    def _on_result(self, report, result):
        self._write_result(result)

    on_success = _on_result
    on_failure = _on_result
    on_error = _on_result
    on_pending = _on_result
    on_notification = _on_result

    def on_finish_test_suite(self, report, test_suite):
        if self.have_test:
            self._write("</report>")
        else:
            self._write("<report/>")
        self._write("\n")
        if self.file:
            self.output.close()

    try:
        unicode
        def _normalize(self, string):
            return unicode(string)
    except:
        def _normalize(self, string):
            return str(string)

    def _write(self, string):
        self.output.write(self._normalize(string))

    def _write_tag(self, indent, name, content):
        if content:
            self._write("%s<%s>%s</%s>\n" % (indent, name,
                                             cgi.escape(str(content)),
                                             name))
        else:
            self._write("%s<%s/>\n" % (indent, name))

    def _write_result(self, result):
        self._write("  <result>\n")
        self._write_test_case(result.test.__class__)
        self._write_test(result.test)
        self._write_tag("    ", "status", result.name)
        self._write_tag("    ", "detail", result.detail())
        self._write_tag("    ", "elapsed", "%f" % result.elapsed)
        self._write_traceback(result.traceback)
        self._write("  </result>\n")

    def _write_test_case(self, test_case):
        name = "%s.%s" % (test_case.__module__, test_case.__name__)
        description = test_case.__doc__
        self._write("    <test_case>\n")
        self._write_tag("      ", "name", name)
        self._write_tag("      ", "description", description)
        self._write("    </test_case>\n")

    def _write_test(self, test):
        self._write("    <test>\n")
        self._write_tag("      ", "name", test.short_name())
        self._write_tag("      ", "description", test.description())
        self._write_test_metadata(test.metadata)
        self._write("    </test>\n")

    def _write_test_metadata(self, metadata):
        if not metadata:
            return
        for key in metadata:
            self._write("      <option>\n")
            self._write_tag("        ", "name", key)
            self._write_tag("        ", "value", metadata[key])
            self._write("      </option>\n")

    def _write_traceback(self, traceback):
        if not traceback:
            return
        self._write("    <backtrace>\n")
        self._write("      <entry>\n")
        for entry in traceback:
            self._write_tag("        ", "file", entry.file_name)
            self._write_tag("        ", "line", entry.line_number)
            self._write_tag("        ", "info", entry.content)
        self._write("      </entry>\n")
        self._write("    </backtrace>\n")
