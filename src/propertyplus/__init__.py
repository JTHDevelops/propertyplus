''' PropertyPlus is a collection of extensions to the `property` built-in.

    The core of the package is the Property class, which is a direct 

'''

import re
from numbers import Number

from typing import Any, Callable, TypeVar, NewType, Union, Tuple, Optional
from typing import ForwardRef, Iterable

from typing_extensions import TypeAlias
from auto_all import start_all, end_all


ValidType       = Any
InvalidType     = Any
ValidValue      = Any
InvalidValue    = Any
NormalizedData  = Any
UnstableData    = Any
UnknownData     = Any

start_all()

try:
    from .property import *
except ImportError as e:
    from propertyplus.property import *

try:
    from .string_properties import *
except ImportError as e:
    from propertyplus.string_properties import *



class NumberProperty(Property):
    '''UNIMPLEMENTED as of yet.'''
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        

class FileProperty(Property):
    '''UNIMPLEMENTED as of yet.'''
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        

    
end_all()


if __name__ == '__main__':
    pass
