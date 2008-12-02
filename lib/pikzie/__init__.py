version = "0.9.3"

if not "sorted" in __builtins__:
    def sorted(iterable, cmd=None, key=None, reverse=False):
        list = iterable[:]
        list.sort(cmd)
        if reverse:
            list.reverse()
        return list
    __builtins__["sorted"] = sorted

from pikzie.tester import Tester
from pikzie.core import *
from pikzie.decorators import *
from pikzie.module_base import *
