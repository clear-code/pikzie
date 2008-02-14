#!/usr/bin/env python

import sys
import os
import glob
import subprocess
import pydoc
import shutil
import gettext

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

class update_po(Command):
    description = "update *.po"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = ["pygettext", "--extract-all", "--default-domain", "pikzie",
                   "--docstrings", "--output-dir", "po"]
        command.extend(glob.glob("lib/*.py"))
        command.extend(glob.glob("lib/*/*.py"))
        command.extend(glob.glob("lib/*/*/*.py"))
        _run(*command)
        for po in glob.glob("po/*.po"):
            _run("msgmerge", "--update", po, "po/pikzie.pot")

class update_mo(Command):
    description = "update *.mo"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for po in glob.glob("po/*.po"):
            (lang, ext) = os.path.splitext(os.path.basename(po))
            mo_dir = os.path.join("data", "locale", lang, "LC_MESSAGES")
            if not os.access(mo_dir, os.F_OK):
                os.makedirs(mo_dir)
            _run("msgfmt", "--output-file", os.path.join(mo_dir, "pikzie.mo"),
                 po)

class update_doc(Command):
    description = "update documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self._generate_assertions_html(None)
        _run("rst2html", "README", "html/readme.html")
        _run("rst2html", "README.ja", "html/readme.html.ja")
        _run("rst2html", "NEWS", "html/news.html")
        _run("rst2html", "NEWS.ja", "html/news.html.ja")

    def _generate_assertions_html(self, lang):
        object = pikzie.assertions.Assertions
        html_name = "html/assertions.html"
        if lang:
            html_name = "%s.%s" % (html_name, lang)
            _ = gettext.translation("pikzie", "data/locale",[lang]).gettext
            for name in dir(object):
                if name.startswith("_"):
                    continue
                method = getattr(object, name)
                method.__doc__ = _(method.__doc__) # Not work :<

        page = pydoc.html.page(pydoc.describe(object),
                               pydoc.html.document(object, "assertions"))
        html = file(html_name, "w")
        html.write(page)
        html.close()

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
        commands.extend(glob.glob("html/*.html*"))
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
             "dist/%s-%s.tar.gz" % (package_name, version),
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
            _run("svn", "cp", "-m", "released %s!!!" % version,
                 "%s/trunk" % sf_repos, "%s/tags/%s" % (sf_repos, version))
        else:
            print "%s is already tagged" % version

setup(name=package_name,
      version=version,
      description="an easy to write/debug Unit Testing Framework for Python",
      author="Kouhei Sutou",
      author_email="kou@cozmixng.org",
      url="http://pikzie.sf.net/",
      download_url="http://sf.net/project/showfiles.php?group_id=215708",
      license="LGPL",
      package_dir={'': 'lib'},
      packages=["pikzie", "pikzie.ui"],
      classifiers=[
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Natural Language :: Japanese",
        "Natural Language :: English",
        ],
      cmdclass={"update_po": update_po,
                "update_mo": update_mo,
                "update_doc": update_doc,
                "upload_doc": upload_doc,
                "release": release,
                "tag": tag})
