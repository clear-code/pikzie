# Copyright (C) 2009  Kouhei Sutou <kou@clear-code.com>
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

import random

class PriorityChecker(object):
    def must():
        return True
    must = staticmethod(must)

    def important():
        return random.random() >= 0.1
    important = staticmethod(important)

    def high():
        return random.random() >= 0.3
    high = staticmethod(high)

    def normal():
        return random.random() >= 0.5
    normal = staticmethod(normal)

    def low():
        return random.random() >= 0.75
    low = staticmethod(low)

    def never():
        return False
    never = staticmethod(never)
