#pylint: disable=W0401

from .exception import *
from .util import *
from .main import *


class Glbl():
    def get(self, key, dflt=None):
        return getattr(self, key, dflt)


g = Glbl()
