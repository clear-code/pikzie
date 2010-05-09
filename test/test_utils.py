# Copyright (C) 2010  Kouhei Sutou <kou@clear-code.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import pikzie
from pikzie.utils import *

tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")

def setup():
    rm_rf(tmp_dir)

def teardown():
    rm_rf(tmp_dir)

def test_mkdir_p():
    deep_dir = os.path.join(tmp_dir, "deep", "dir")
    assert_not_exists(deep_dir)
    mkdir_p(deep_dir)
    assert_exists(deep_dir)

def test_rm_rf():
    deep_dir = os.path.join(tmp_dir, "deep", "dir")
    deep_file = os.path.join(deep_dir, "file")
    mkdir_p(deep_dir)
    assert_open_file(deep_file, "w")
    assert_exists(tmp_dir)
    rm_rf(tmp_dir)
    assert_not_exists(tmp_dir)

def test_cp_a():
    source_dir = os.path.join(tmp_dir, "src")
    shallow_copy = os.path.join(source_dir, "file")
    deep_dir = os.path.join(source_dir, "deep", "dir")
    deep_file = os.path.join(deep_dir, "file")
    mkdir_p(deep_dir)
    assert_open_file(shallow_copy, "w")
    assert_open_file(deep_file, "w")

    destination_dir = os.path.join(tmp_dir, "dest")
    assert_not_exists(destination_dir)
    cp_a(source_dir, destination_dir)
    assert_exists(destination_dir)
    tree = []
    for root, dirs, files in os.walk(destination_dir):
        for base in dirs + files:
            tree.append(os.path.join(root, base))
    assert_equal(sorted([os.path.join(destination_dir, "file"),
                         os.path.join(destination_dir, "deep"),
                         os.path.join(destination_dir, "deep", "dir"),
                         os.path.join(destination_dir, "deep", "dir", "file")]),
                 sorted(tree))
