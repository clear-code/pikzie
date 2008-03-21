import re
from StringIO import StringIO
import pikzie
import pikzie.report
import pikzie.ui.console
from test.utils import *

ConsoleTestRunner = pikzie.ui.console.ConsoleTestRunner
VERBOSE_LEVEL_SILENT = pikzie.ui.console.VERBOSE_LEVEL_SILENT

class TestXMLReport(pikzie.TestCase, Assertions):
    """Tests for XML report."""

    class TestCase(pikzie.TestCase, Assertions):
        def _test_success(self):
            self.assert_true(True)

        TEST_FAILURE_LINE = Source.current_line_no() + 2
        def _test_failure(self):
            self.assert_true(False)
        _test_failure = pikzie.bug(1234)(_test_failure)

        TEST_ERROR_LINE = Source.current_line_no() + 2
        def _test_error(self):
            self.non_existence_method()

    def test_empty_test(self):
    	self.assert_xml("<report/>\n", self._suite())

    def test_success_result(self):
        elapsed = "0.001"
        xml = """
<report>
  <result>
    <test_case>
      <name>test.test_xml_report.TestCase</name>
      <description/>
    </test_case>
    <test>
      <name>_test_success</name>
      <description/>
    </test>
    <status>success</status>
    <detail/>
    <elapsed>%s</elapsed>
  </result>
</report>
"""
        xml = (xml.strip() + "\n") % elapsed
        self.assert_xml(xml, self._suite(["_test_success"]), elapsed)

    def test_failure_result(self):
        elapsed = "0.001"
        backtrace_line = Source.current_line_no() + 1
        xml = """
<report>
  <result>
    <test_case>
      <name>test.test_xml_report.TestCase</name>
      <description/>
    </test_case>
    <test>
      <name>_test_failure</name>
      <description/>
      <option>
        <name>bug</name>
        <value>1234</value>
      </option>
    </test>
    <status>failure</status>
    <detail>expected: &lt;False&gt; is a true value</detail>
    <elapsed>%s</elapsed>
    <backtrace>
      <entry>
        <file>%s</file>
        <line>%s</line>
        <info>self.assert_true(False)</info>
      </entry>
    </backtrace>
  </result>
</report>
"""
        file = Source.current_file()
        xml = xml % (elapsed, file, self.TestCase.TEST_FAILURE_LINE)
        xml = xml.strip() + "\n"
        self.assert_xml(xml, self._suite(["_test_failure"]), elapsed)

    def _suite(self, names=[]):
        return pikzie.TestSuite([self.TestCase(name) for name in names])

    TEST_RUN_LINE = Source.current_line_no() + 3
    def assert_xml(self, expected, suite, normalized_elapsed=None):
        runner = ConsoleTestRunner(verbose_level=VERBOSE_LEVEL_SILENT)
        report_output = StringIO()
        report = pikzie.report.XML(report_output)
        result = runner.run(suite, [report])
        report_output.seek(0)
        xml = report_output.read()
        if xml and normalized_elapsed:
            xml = re.sub(r"<elapsed>[\d.]+<\/elapsed>",
                         "<elapsed>%s</elapsed>" % normalized_elapsed,
                         xml)
        self.assert_equal(expected, xml)
