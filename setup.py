#!/usr/bin/env python

import sys
import os
import re
import glob
import subprocess
import pydoc
import shutil
import gettext
try:
    import setuptools
except ImportError:
    pass

from distutils.core import setup
from distutils.cmd import Command
from distutils.dist import DistributionMetadata

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import pikzie

package_name = "Pikzie"
distribution_name = package_name.lower()
version = pikzie.version
sf_project_name = "Pikzie"
sf_package_name = package_name.lower()
sf_user = "ktou"
sf_host = "%s@web.sourceforge.net" % sf_user
sf_repos = "https://%s@pikzie.svn.sourceforge.net/svnroot/pikzie" % sf_user
sf_htdocs = "/home/groups/p/pi/pikzie/htdocs"

long_description = re.split("\n.+\n=+", open("README").read())[5].strip()
description = re.sub("\n", " ", long_description.split("\n\n")[0])

def get_fullname(self):
    return "%s-%s" % (distribution_name, self.get_version())
DistributionMetadata.get_fullname = get_fullname

def _run(*command):
    return_code = _run_without_check(*command)
    if return_code != 0:
        raise RuntimeError, \
            "failed to run <%d>: %s" % (return_code, " ".join(command))

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
        import textwrap
        command = ["pygettext", "--extract-all", "--default-domain", "pikzie",
                   "--docstrings", "--output-dir", "po"]
        command.extend(glob.glob("lib/*.py"))
        command.extend(glob.glob("lib/*/*.py"))
        command.extend(glob.glob("lib/*/*/*.py"))
        _run(*command)

        pot = file("po/pikzie.pot", "r").read()
        docstring_msgid_re = re.compile("^#, docstring\nmsgid(.+?)^msgstr",
                                        re.M | re.DOTALL)
        def strip_spaces(match_object):
            docstring = match_object.group(1).strip()
            docstring = re.compile("^\"|\"$", re.M).sub("", docstring)
            docstring = re.sub("\n", "", docstring)
            docstring = re.sub(r"(?<!\\)\\n", "\n", docstring)
            docstring = textwrap.dedent(docstring).strip()
            docstring = re.compile("^(.*?)$", re.M).sub(r'"\1\\n"', docstring)
            docstring = re.sub("\\\\n\"$", "\"", docstring)
            return "#, docstring\nmsgid \"\"\n%s\nmsgstr" % docstring
        pot = docstring_msgid_re.sub(strip_spaces, pot)
        pot_file = file("po/pikzie.pot", "w")
        pot_file.write(pot)
        pot_file.close()

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
        self._generate_assertions_html("ja")
        _run("rst2html", "README", "html/readme.html")
        _run("rst2html", "README.ja", "html/readme.html.ja")
        _run("rst2html", "NEWS", "html/news.html")
        _run("rst2html", "NEWS.ja", "html/news.html.ja")

    def _generate_assertions_html(self, lang):
        object = pikzie.assertions.Assertions
        html_name = "html/assertions.html"
        translation = None
        if lang:
            html_name = "%s.%s" % (html_name, lang)
            translation = gettext.translation("pikzie", "data/locale", [lang])

        print html_name

        original_getdoc = pydoc.getdoc
        def getdoc(object):
            document = original_getdoc(object)
            if document == "":
                return document
            else:
                return translation.gettext(document)
        if translation:
            pydoc.getdoc = getdoc
        page = pydoc.html.page(pydoc.describe(object),
                               pydoc.html.document(object, "assertions"))
        pydoc.getdoc = original_getdoc

        html = file(html_name, "w")
        html.write(page.strip())
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
        html_files = glob.glob("html/*.html*")
        for html in html_files:
            if html.startswith("html/index.html"):
                continue
            if html.endswith(".ja"):
                footer = file("html/footer.ja").read()
            else:
                footer = file("html/footer").read()
            self._prepare_html(html, footer)
        commands = ["scp"]
        commands.extend(html_files)
        commands.append("html/pikzie.css")
        commands.append("%s:%s/" % (sf_host, sf_htdocs))
        _run(*commands)

    def _prepare_html(self, html, footer):
        html_file = file(html, "rw+")
        content = html_file.read()
        content = re.sub("</head>",
                         r'<link rel="stylesheet" href="pikzie.css" type="text/css" />\n' +
                         r'</head>',
                         content)
        content = re.sub("<body([^>]*?)>",
                         r'<body\1><div class="main">\n',
                         content)
        content = re.sub("</body>",
                         r'</div>\n%s\n</body>' % footer,
                         content)
        html_file.seek(0)
        html_file.write(content)
        html_file.close

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
        _run("misc/release.rb", sf_user, sf_project_name, sf_package_name,
             version, "dist/%s.tar.gz" % self.distribution.get_fullname(),
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

download_url = "http://downloads.sourceforge.net/pikzie/pikzie-%s.tar.gz" % version
setup(name=package_name,
      version=version,
      description=description,
      long_description=long_description,
      author="Kouhei Sutou",
      author_email="kou@cozmixng.org",
      url="http://pikzie.sourceforge.net/",
      download_url=download_url,
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
