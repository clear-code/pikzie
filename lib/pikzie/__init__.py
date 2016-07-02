# Copyright (C) 2009-2016  Kouhei Sutou <kou@clear-code.com>
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

version = "1.0.3"

try:
    import __builtin__
except ImportError:
    pass
else:
    if not hasattr(__builtin__, "sorted"):
        def sorted(iterable, cmd=None, key=None, reverse=False):
            list = iterable[:]
            list.sort(cmd)
            if reverse:
                list.reverse()
                return list
        __builtin__.sorted = sorted

from pikzie.tester import Tester
from pikzie.core import *
from pikzie.decorators import *
from pikzie.module_base import *
from pikzie.utils import *
