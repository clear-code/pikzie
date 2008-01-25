#!/usr/bin/env python

import sys
import os

from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

import pikzie

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
        ])
