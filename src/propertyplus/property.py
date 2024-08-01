import re
from typing import Any, Callable, Union, Tuple, Optional, Iterable
from typing_extensions import TypeVar

from auto_all import start_all, end_all

ValidType       = TypeVar('ValidType')
InvalidType     = TypeVar('InvalidType')
ValidValue      = TypeVar('ValidValue')
InvalidValue    = TypeVar('InvalidValue')
NormalizedData  = TypeVar('NormalizedData')
UnstableData    = TypeVar('UnstableData')
UnknownData     = TypeVar('UnknownData')

start_all()
class Property(property):
    '''
    Property(...) -> property attribute.
        See Property.__init__ for initialization details.
        
    Return an automatically managed Property descriptor.
    
    Typical use to define a managed property, 'x':

    class C:
        @Property("The 'x' Property")
        def x(self):
            \'''With detailed documentation.\'''

    Comparison between classic property 'x' and Property 'y':
      
    class Point:

        @property
        def x(self):
            \'''This is the 'x' property, which is implemented using the classic property decorator.
            \'''
            if not hasattr(self, '_x'):
                setattr(self, '_x', None)
            return self._x

        @x.setter
        def x(self, value):
            self._x = value

        @x.deleter
        def x(self):
            del self._x


        @Property("This is the 'y' Property.")
        def y(self):
            \'''Identical in functionality to the 'x' property, but faster
                and more efficient.\'''
            '''
    fget        = None
    fset        = None
    fdel        = None
    fdoc        = None
    fval        = None
    ffix        = None
    fnrm        = None
    fagetter    = None
    fpgetter    = None
    fasetter    = None
    fpsetter    = None
    fadeleter   = None
    fpdeleter   = None    
    

    def __new__(cls, *args, **kwargs):
        '''Instantiate the Property object as a blank property.
            Returns an object equivalent to property().
        '''
        return super().__new__(cls)
    
    def __init__(self, /,
                 fget: Optional[Union[Callable[[], Any],str,None]]                  = None,
                 fset: Optional[Callable[[Any], None]]                              = None,
                 fdel: Optional[Callable[[], None]]                                 = None,
                 docs: Optional[Union[str, None]]                                   = None,
                 fval: Optional[Callable[[Union[ValidValue, InvalidValue]], bool]]  = None,
                 ffix: Optional[Callable[[InvalidType], ValidType]]                 = None,
                 fnrm: Optional[Callable[[UnstableData], NormalizedData]]           = None,
                 *,
                 types: Union[type, Tuple[Union[type, None]], None]                 = None,
                 default: Any                                                       = None,
                 values: Iterable[ValidValue]                                       = None,
                 readonly:  bool                                                    = False,
                 indelible: bool                                                    = False,
                 blackhole: bool                                                    = False,
                 cachename: str                                                     = None,
                 **kwargs
                 ):
        '''    
        Initializes a new instance of the Property class.

        Args:
            fget (Callable or str, optional): 
                The getter function for the property or the documentation 
                string.
                
            fset (Callable, optional): 
                The setter function for the property.
                
            fdel (Callable, optional): 
                The deleter function for the property.
                
            docs (str, optional): 
                The documentation string for the property.
                
            fval (Callable, optional): 
                The validation function for the property. This function 
                should expect the value to be set as an argument and return
                a boolean:
                    True if the value is valid, False otherwise.
                    
            ffix (Callable, optional): 
                The fix function for the property. This function is called 
                when the property's value is set to a value of an incorrect 
                type. The function should take a value of any type as an 
                argument and return an approximately equivalent value of 
                the correct type.
                
            fnrm (Callable, optional): 
                The normalization function for the property.
                
            types (type or Tuple[type], optional): 
                The expected type or a tuple of acceptable types of the 
                property's value.
                
            default (Any, optional): 
                The default value for the property.  This will default 
                to None.
            
            values (Iterable[ValidValue], optional): 
                If present, values should be a set (or other iterable)
                of all acceptable values.
                
            readonly (bool, optional): 
                Whether the property is read-only (has no setter).
                
            indelible (bool, optional): 
                Whether the property is indelible (has no deleter).
                
            blackhole (bool, optional): 
                Whether the property is a blackhole (has no getter).
                
            cachename (str, optional): 
                The name of the hidden cache for the property. 
                This will default to f'_{property_name}'.
        
        NOTES:
        If {fget} is a string, it is used as the first line/part of the
            documentation for the property and `fget` is set to None.

        If {fget} is a callable and all other arguments are None or False, 
        the property is set to read-only.

        '''
        
        # Handle {fget}
        if isinstance(fget, str):
            docs = f"{fget}\n{('' if docs is None else docs)}"
            fget = None
            
        if (isinstance(fget, Callable) and
            (set((fset, fdel, docs, fval, ffix, fnrm,
                  types, default, readonly, indelible, blackhole,
                  cachename)
                 )=={None, False})
            ):
            readonly = True
        
        # Handle explicit read-only, indelible, or blackhole
        self.readonly  = True if kwargs.get('ro', readonly)  else False
        self.indelible = True if kwargs.get('nd', indelible) else False
        self.blackhole = True if kwargs.get('bh', blackhole) else False
        
        self.fget = None if self.blackhole else (
            self.default_getter if (fget is None ) else fget)
        
        self.fset = None if self.readonly else (
            self.default_setter if fset is None else fset)
            
        self.fdel = None if self.indelible else (
            self.default_deleter if fdel is None else fdel)
            
        self.fdoc      = None
        self.docs      = docs if isinstance(docs, str) else ''
        self.fval      = fval 
        self.fnrm      = fnrm
        self.ffix      = ffix
        
        
        self.types     = types if (types is None or (
            isinstance(types, tuple) and (
                sum([0 if isinstance(T, type) or T is None else 1 for T in types])==0)
            )) else (types,) if isinstance(types, type) else None
        if isinstance(self.types, tuple):
            if None in self.types:
                self.types=tuple([T if T is not None else type(T) for T in self.types])
                
        self.default   = default
        self.values    = values
        
        if cachename is not None:
            if re.match('^[A-z]+[A-z0-9_]*$', cachename):
                self._name = f'_{cachename}'
            else:
                raise ValueError(f'Invalid value for cachename, {cachename},  must match the pattern ^[A-z]+[A-z0-9_]*$')
            
        self.gen__doc__()
        
        
    def __set_name__(self, owner: type, name: str) -> None:
        '''Set the name of the Property and the Property's cache variable
            which defaults to f'_{name}'.
            
        '''
        self.name  = name
        self._name = getattr(self, '_name', f'_{self.name}')
        self.owner = owner

    def __get__(self, obj: Any, owner: type) -> ValidValue:
        '''Wrapper for the property's getter, stored in fget.'''
        if obj is None:
            return
        if self.fget is None:
            raise AttributeError('This attribute is illegible.')
        if self.fagetter is not None:
            self.fagetter(obj)
        if self.fpgetter is not None:
            return self.fpgetter(self.fget(obj))
        return self.fget(obj)

    def default_getter(self, obj: Any) -> ValidValue:
        ''''''
        if not hasattr(obj, self._name):
            setattr(obj, self._name, self.default)
        return getattr(obj, self._name)

    def __set__(self, obj: Any, val: UnknownData) -> None:
        '''Wrapper to implement the use of ffix,  fnrm, fval, and fset.'''
        if self.fset is None:
            raise AttributeError('This attribute is read-only.')
        if self.types is not None:
            if not isinstance(val, self.types):
                if isinstance(self.ffix, Callable):
                    val = self.ffix(obj, val)
                else:
                    raise TypeError(
                        f'Incompatible value type for {obj.__class__.__name__}.{self.name}'
                        )
        if isinstance(self.fnrm, Callable):
            val = self.fnrm(obj, val)
        if isinstance(self.fval, Callable):
            if not self.fval(obj, val):
                raise ValueError(
                    f'Incompatible value {val} for property {obj.__class__.__name__}.{self.name}.'
                    )
        if self.fasetter is not None:
            val = self.fasetter(obj, val)
        self.fset(obj, val)
        if self.fpsetter is not None:
            self.fpsetter(obj, val)

    def default_setter(self, obj:Any, val: ValidValue) -> None:
        ''''''
        if obj is None:
            return
        setattr(obj, self._name, val)
        
    def __delete__(self, obj:Any) -> None:
        '''Wrapper for the property's deleter, referenced in fdel.'''
        if self.fdel is None:
            raise AttributeError('This attribute is indelible.')
        if self.fadeleter is not None:
            self.fadeleter(obj)
        self.fdel(obj)
        if self.fpdeleter is not None:
            self.fpdeleter(obj)


    def default_deleter(self, obj: Any) -> None:
        delattr(obj, self._name)


    def __call__(
        self,
        fdoc: Callable[[], None]
        ) -> 'Property':
        '''Decorator alias for documentor.'''
        return self.documentor(fdoc)

    def getter(
        self,
        fget: Callable[[], Any]
        ) -> 'Property':
        '''Decorator to set the getter.'''
        self.fget = fget
        self.blackhole = False
        self.gen__doc__()
        return self
    
    def setter(
        self,
        fset: Callable[[Any], None]
        ) -> 'Property':
        '''Decorator to set the setter.'''
        self.fset = fset
        self.readonly = False
        self.gen__doc__()
        return self
    
    def deleter(
        self,
        fdel: Callable[[], None]
        ) -> 'Property':
        '''Decorator to set the deleter.'''
        self.fdel = fdel
        self.indelible = False
        self.gen__doc__()
        return self
    
    def documentor(
        self,
        fdoc: Callable[[], None]
        ) -> 'Property':
        '''Decorator to set the documentor.'''
        self.fdoc = fdoc
        self.gen__doc__()
        return self

    def validator(
        self,
        fval: Callable[[Union[ValidValue, InvalidValue]], bool]
        ) -> 'Property':
        '''Decorator to set the validator.'''
        self.fval = fval
        self.gen__doc__()
        return self

    def normalizer(
        self,
        fnrm: Callable[[UnstableData], NormalizedData]
        ) -> 'Property':
        '''Decorator to set the normalizer.'''
        self.fnrm = fnrm
        self.gen__doc__()
        return self

    def typefixer(
        self,
        ffix: Callable[[InvalidType], ValidType]
        ) -> 'Property':
        '''Decorator to set the type corrector.'''
        self.ffix = ffix
        self.gen__doc__()
        return self

    def antegetter(self, fagetter: Callable[[], Any]) -> 'Property':
        '''Decorator to set the antegetter.'''
        self.fagetter = fagetter
        self.gen__doc__()
        return self
    
    def postgettter(self, fpgetter: Callable[[Any], Any]) -> 'Property':
        '''Decorator to set the postgetter.'''
        self.fpgetter = fpgetter
        self.gen__doc__()
        return self
        
    def antesetter(self, fasetter: Callable[[Any], Any]) -> 'Property':
        '''Decorator to set the antesetter.'''
        self.fasetter = fasetter
        self.gen__doc__()
        return self
    
    def postsetter(self, fpsetter: Callable[[Any], Any]) -> 'Property':
        '''Decorator to set the postsetter.'''
        self.fpsetter = fpsetter
        self.gen__doc__()
        return self
    
    def antedeleter(self, fadeleter: Callable[[], None]) -> 'Property':
        '''Decorator to set the antedeleter.'''
        self.fadeleter = fadeleter
        self.gen__doc__()
        return self
    
    def postdeleter(self, fpdeleter: Callable[[], None]) -> 'Property':
        '''Decorator to set the postdeleter.'''
        self.fpdeleter = fpdeleter
        self.gen__doc__()
        return self
    

    def gen__doc__(self):
        '''Generate the __doc__ for the property.
            Called at the end of __init__ and each decorator function.
        '''
        docstr  = self.docs if self.docs is not None else ''    
        types   = '' if self.types   is None else f":    Type-Restricted: {', '.join([T.__name__ for T in self.types])}"
        default = '' if self.default is None else f':      default value: {self.default}'
        docf = getattr(self.fget, '__doc__', '')
        docs = getattr(self.fset, '__doc__', '')
        docd = getattr(self.fdel, '__doc__', '')
        docc = getattr(self.fdoc, '__doc__', '')
        docv = getattr(self.fval, '__doc__', '')
        docn = getattr(self.fnrm, '__doc__', '')
        docx = getattr(self.ffix, '__doc__', '')
        documents = ['' if doc is None else (
            f'{doc}\n' if len(doc) else doc
            ) for doc in (
                docstr, docf, docs, docd, docc,
                docv, docn, docx,
                '' if ((self.types is None) and
                       (self.default is None)) else ('-'*66),
                types, default)
            ]
        self.__doc__ = ''.join(documents)


def getter(prop):
    '''Decorator to set the getter for {prop}.'''
    return prop.getter

def setter(prop):
    '''Decorator to set the setter for {prop}.'''
    return prop.setter
    
def deleter(prop):
    '''Decorator to set the deleter for {prop}.'''
    return prop.deleter
    
def documentor(prop):
    '''Decorator to set the documentor for {prop}.'''
    return prop.documentor

def validator(prop):
    '''Decorator to set the validator for {prop}.'''
    return prop.validator

def normalizer(prop):
    '''Decorator to set the normalizer for {prop}.'''
    return prop.normalizer

def typefixer(prop):
    '''Decorator to set the typefixer for {prop}.'''
    return prop.typefixer


def antegetter(prop):
    '''Decorator to set the antegetter for {prop}.'''
    return prop.antegetter

def postgetter(prop):
    '''Decorator to set the postgetter for {prop}.'''
    return prop.postgetter


def antesetter(prop):
    '''Decorator to set the antesetter for {prop}.'''
    return prop.antesetter

def postsetter(prop):
    '''Decorator to set the postsetter for {prop}.'''
    return prop.postsetter
    

def antedeleter(prop):
    '''Decorator to set the antedeleter for {prop}.'''
    return prop.antedeleter

def postdeleter(prop):
    '''Decorator to set the postdeleter for {prop}.'''
    return prop.postdeleter

end_all()

