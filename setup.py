#!/usr/bin/env python

import sys
import os
import subprocess

from distutils.core import setup
from distutils.cmd import Command

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import pikzie

sf_user = "ktou"
sf_host = "%s@shell.sourceforge.net" % sf_user
sf_htdocs = "/home/groups/p/pi/pikzie/htdocs"

class upload_doc(Command):
    description = "upload documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self._run("scp", "html/index.html",
                  "%s:%s/index.html" % (sf_host, sf_htdocs))
        self._run("rst2html", "README", "html/readme.html")
        self._run("rst2html", "README.ja", "html/readme.html.ja")
        self._run("scp", "html/readme.html", "html/readme.html.ja",
                  "%s:%s/" % (sf_host, sf_htdocs))
        self._run_without_check("ssh", sf_host, "chmod", "-R", "g+w", sf_htdocs)

    def _run(self, *command):
        if self._run_without_check != 0:
            raise "failed to run: %s" % " ".join(command)

    def _run_without_check(self, *command):
        return subprocess.call(command)

setup(name="pikzie",
      version=pikzie.version,
      description="an easy to write/debug Unit Testing Framework for Python",
      author="Kouhei Sutou",
      author_email="kou@cozmixng.org",
      url="http://pikzie.sf.net/",
      license="LGPL",
      package_dir = {'': 'lib'},
      packages=["pikzie"],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Testing",
        ],
      cmdclass={"upload_doc": upload_doc})
