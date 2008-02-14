version = "0.4.0"

if not hasattr(__builtins__, "sorted"):
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
