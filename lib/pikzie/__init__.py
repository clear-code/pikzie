import __builtin__

version = "0.9.4"

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
