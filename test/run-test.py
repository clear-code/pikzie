#!/usr/bin/env python

import sys
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(base_dir, "lib"))
sys.path.insert(0, base_dir)

import pikzie

pikzie.main()
