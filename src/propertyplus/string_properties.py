import re
 
from typing import Union, Optional, Callable, TypeVar

from auto_all import start_all, end_all


try:
    from .properties import *
except ImportError as e:
    from propertyplus.properties import *

start_all()
class StringProperty(Property):
    def __init__(
        self, 
        docstr: Optional[str]=None, 
        validator: Optional[Callable[[Union[ValidValue, InvalidValue]], bool]] = None, 
        normalizer: Optional[Callable[[UnknownData], NormalizedData]] = None, 
        pattern: Union[str, re.Pattern]=None, 
        valueset: list[str] = None,
        **k
        ):
        
        super().__init__(docstr, fval=validator, fnrm=normalizer, values=valueset, **k)
        
class URLProperty(StringProperty):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
class EmailProperty(StringProperty):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
        
end_all()


