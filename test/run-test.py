#!/usr/bin/env python

import sys
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(base_dir, "lib"))
sys.path.insert(0, base_dir)

import pikzie

sys.argv.insert(1, "--ignore-directory")
sys.argv.insert(2, "fixtures")
sys.exit(pikzie.Tester(version=pikzie.version).run())
