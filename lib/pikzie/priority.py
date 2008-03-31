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
