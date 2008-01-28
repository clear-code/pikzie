#!/usr/bin/env python

import sys
import os
import subprocess

from distutils.core import setup
from distutils.cmd import Command

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import pikzie

package_name = "pikzie"
version = pikzie.version
sf_project_name = "pikzie"
sf_user = "ktou"
sf_host = "%s@shell.sourceforge.net" % sf_user
sf_htdocs = "/home/groups/p/pi/pikzie/htdocs"

def _run(*command):
    if _run_without_check != 0:
        raise "failed to run: %s" % " ".join(command)

def _run_without_check(*command):
    print " ".join(command)
    return subprocess.call(command)

class upload_doc(Command):
    description = "upload documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        _run("scp", "html/index.html",
             "%s:%s/index.html" % (sf_host, sf_htdocs))
        _run("rst2html", "README", "html/readme.html")
        _run("rst2html", "README.ja", "html/readme.html.ja")
        _run("scp", "html/readme.html", "html/readme.html.ja",
             "%s:%s/" % (sf_host, sf_htdocs))
        _run_without_check("ssh", sf_host, "chmod", "-R", "g+w", sf_htdocs)

class release(Command):
    description = "release package to SF.net"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sdist = self.reinitialize_command("sdist")
        self.run_command("sdist")
        _run("misc/release.rb", sf_user, sf_project_name, version,
             "%s-%s.tar.gz" % (package_name, version),
             "README", "NEWS")

setup(name=package_name,
      version=version,
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
      cmdclass={"upload_doc": upload_doc,
                "release": release})
