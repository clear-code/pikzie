class XML(object):
    def __init__(self, output):
        self.output = output
        self.results = []

    def on_finish_test_suite(self, report, test_suite):
        self.output.write("<report/>")
