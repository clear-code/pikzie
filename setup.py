#!/usr/bin/env python

import sys
import os
import glob
import subprocess
import pydoc
import shutil

from distutils.core import setup
from distutils.cmd import Command

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import pikzie

package_name = "pikzie"
version = pikzie.version
sf_project_name = "pikzie"
sf_user = "ktou"
sf_host = "%s@shell.sourceforge.net" % sf_user
sf_repos = "https://%s@pikzie.svn.sourceforge.net/svnroot/pikzie" % sf_user
sf_htdocs = "/home/groups/p/pi/pikzie/htdocs"

def _run(*command):
    return_code = _run_without_check(*command)
    if return_code != 0:
        raise "failed to run <%d>: %s" % (return_code, " ".join(command))

def _run_without_check(*command):
    print " ".join(command)
    return subprocess.call(command)

class update_doc(Command):
    description = "update documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pydoc.writedoc(pikzie.assertions.Assertions)
        shutil.move("Assertions.html", "html/")
        _run("rst2html", "README", "html/readme.html")
        _run("rst2html", "README.ja", "html/readme.html.ja")

class upload_doc(Command):
    description = "upload documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sdist = self.reinitialize_command("update_doc")
        self.run_command("update_doc")
        commands = ["scp"]
        commands.extend(glob.glob("html/*.html"))
        commands.append("%s:%s/" % (sf_host, sf_htdocs))
        _run(*commands)
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

class tag(Command):
    description = "tag %s" % version
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            _run("svn", "ls", "%s/tags/%s" % (sf_repos, version))
        except:
            print "%s is already tagged" % version
        else:
            _run("svn", "cp", "-m", "released %s!!!" % version,
                 "%s/trunk" % sf_repos, "%s/tags/%s" % (sf_repos, version))

setup(name=package_name,
      version=version,
      description="an easy to write/debug Unit Testing Framework for Python",
      author="Kouhei Sutou",
      author_email="kou@cozmixng.org",
      url="http://pikzie.sf.net/",
      license="LGPL",
      package_dir={'': 'lib'},
      packages=["pikzie"],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Testing",
        ],
      cmdclass={"update_doc": update_doc,
                "upload_doc": upload_doc,
                "release": release,
                "tag": tag})
