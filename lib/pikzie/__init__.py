version = "0.2.0"

if not hasattr(__builtins__, "sorted"):
    def sorted(iterable):
        list = iterable[:]
        list.sort()
        return list
    __builtins__["sorted"] = sorted

from pikzie.tester import Tester
from pikzie.core import *
