from auto_all import start_all, end_all


try:
    from .property import Property
except ImportError as e:
    from propertyplus.property import Property

start_all()
class StringProperty(Property):
    def __init__(
        self, 
        docstr: Union[str, None]=None, 
        validator=None, 
        normalizer=None, 
        pattern=None, 
        valueset=None
        **k
        ):
        
        super().__init__(docstr, fval=validator, fnrm=normalizer, values=valueset, **k)
        
class URLProperty(Property):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
class EmailProperty(Property):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
        
end_all()


