from enum import Enum

Debug = True

class TapeType(Enum):
    TCLASS = 1,
    TFUNCTION = 2,
    TPROPERTY = 3,

class Path():
    def __init__(self, local_root, filename, abs_path):
        self._local_root = local_root
        self._filename = filename
        self._abs_path = abs_path

    @property
    def local_root(self):
        return self._local_root
    @property

    def filename(self):
        return self._filename
    
    @property
    def abs_path(self):
        return self._abs_path
    
    def __str__(self):
        return self._abs_path
    
    def __repr__(self):
        return self._abs_path