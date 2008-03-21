import cgi

class XML(object):
    def __init__(self, output):
        self.file = isinstance(output, str)
        if self.file:
            output = file(output, "w")
        self.output = output
        self.have_test = False

    def on_start_test(self, report, test):
        if not self.have_test:
            self.have_test = True
            self._write("<report>\n")

    def on_success(self, report, success):
        self._write_result(success)

    def on_finish_test_suite(self, report, test_suite):
        if self.have_test:
            self._write("</report>")
        else:
            self._write("<report/>")
        self._write("\n")
        if self.file:
            self.output.close()

    def _write(self, string):
        self.output.write(string)

    def _write_tag(self, indent, name, content):
        if content:
            self._write("%s<%s>%s</%s>\n" % (indent, name,
                                             cgi.escape(content), name))
        else:
            self._write("%s<%s/>\n" % (indent, name))

    def _write_result(self, result):
        self._write("  <result>\n")
        self._write_test_case(result.test.__class__)
        self._write_test(result.test)
        self._write_tag("    ", "status", result.name)
        self._write_tag("    ", "detail", result.detail())
        self._write_tag("    ", "elapsed", "%.4f" % result.elapsed)
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
        self._write("    </test>\n")
