import sys, re, inspect

from typing import Callable, Iterable, Union, Optional, Any
from typing import TypeVar, _UnionGenericAlias


NoneType = type(None)


class Property(property):
    '''Subclass of property with default getter, setter, and deleter.
    
        @Property decorates the documentor function: whose docstring pro-
        vides the primary documentation for the Property; whose return 
        value is the Property's default value; and whose return type an-
        notation sets a type-restriction on the Property.
                
        Typical Usage:
        #...
        class Example:
        #...
            @Property
            def text(self) -> str: 
                \'''The text of the Example.
                \'''
                return ''
            
            @Property()
            def number(self)-> (Number, str):
                \'''The number of the Example.
                \'''
                return None
        #...
        # Provides documentation
        #...
            text
                The text of the Example
                TYPE-RESTRICTED: str
                default: ''
            
            number
                The number of the Example.
                TYPE-RESTRICTED: Number, str, None
                default: None
    '''
    fget = None
    fset = None
    fdel = None
    docs = None
    fdoc = None
    default = None
    types = None
    read_only = False
    indelible = False
    illegible = False
    unsettable = False

    
    def __new__(cls, *args, **kwargs):
        '''Create a new Property instance.'''
        return super().__new__(cls)
    
    def _set_types(self, types):
        ''''''
        if isinstance(types, type):
            types = (types,)
        if types is None or isinstance(types, tuple):
            self.types = types
        elif isinstance(types, Iterable):
            if not sum([0 if isinstance(t, (type, NoneType)) else 1 for t in types]):
                self.types = tuple(types)
        if isinstance(self.types, tuple):
            self.unsettable = True if self.default is None or None in self.types or NoneType in self.types or self._unsettable else False
            self.types = tuple(set([NoneType if T is None else T for T in self.types]+[NoneType if self.default is None else self.types[0]]))
            if not self.unsettable:
                if NoneType in self.types:
                    s = set(self.types)
                    s.discard(NoneType)
                    s.discard(None)
                    self.types = tuple(s)

        else:
            self.unsettable=True
            self.types=None
        
        
    def __init__(
        self,
        fdoc = None,
        fget = None, 
        fset = None, 
        fdel = None, 
        docs = None, 
        default = None,
        types = None,
        readonly = None,
        indelible = None,
        illegible = None,
        unsettable = None,
        cachename = None,
        **kwargs
        ):
        '''Initialize the new Property object.
            
            Positional Arguments:
                fdoc -- the documentor function, or a one-line docstring.
                    (defaults to None)
                fget -- the getter function 
                    (defaults to Property.default_getter)
                fset -- the setter function 
                    (defaults to Property.default_setter)
                fdel -- the getter function 
                    (defaults to Property.default_deleter)
                docs -- a documentation string.
                
        '''
        
        self.read_only = True if kwargs.get('readonly', readonly) else False
        self.indelible = True if kwargs.get('indelible', indelible) else False
        self.illegible = True if kwargs.get('illegible', illegible) else False
        
        if isinstance(fdoc, str):
            self.docs = fdoc if not isinstance(docs, str) or not docs.strip() else f'{docs}\n{fdoc}'
            self.fdoc = None
        else:
            self.docs = docs if isinstance(docs, str) else ''
        
        self.fget = None if self.illegible else fget if isinstance(fget, Callable) else self.default_getter
        self.fset = None if self.read_only else fset if isinstance(fset, Callable) else self.default_setter
        self.fdel = None if self.indelible else fdel if isinstance(fdel, Callable) else self.default_delete
        self.fdoc = fdoc if isinstance(fdoc, Callable) else None
        self.default = default
        self._unsettable = unsettable                
        self._set_types(types)

        cachename = kwargs.get('cachename', cachename)
        if isinstance(cachename, str):
            self._name = cachename
        if isinstance(fdoc, Callable):
            self.documentor(fdoc)
        else:
            self.gen__doc__()
        
    
    
        
    def __set_name__(self, owner:type, name:str):
        self.name = name
        self.owner = owner
        self._name = getattr(self, '_name', f'_{self.name}')
    
    def __get__(self, obj: Any = None, owner: type = None):
        '''Getter wrapper.'''
        if obj is None:
            return self
        if self.illegible or self.fget is None:
            raise AttributeError(f'Property {owner.__qualname__}.{self.name} is illegible.')
        return self.fget(obj)
    
    def default_getter(self, obj):
        if not hasattr(obj, self._name):
            setattr(obj, self._name, self.default)
        return getattr(obj, self._name)
        
    def __set__(self, obj:Any, val:Any):
        '''Setter wrapper.'''
        if self.read_only or self.fset is None:
            raise AttributeError(f'Property {obj.__class__.__qualname__}.{self.name} is READ-ONLY!')
        if val is None:
            if not self.unsettable:
                val = self.default
        if self.types is not None:
            if not isinstance(val, self.types):
                raise TypeError(f'Improper type `{type(val).__qualname__}` for Property {obj.__class__.__qualname__}.{self.name}.  Must be one of {", ".join([getattr(t, "__qualname__", repr(t)) for t in self.types])}')
        self.fset(obj, val)
    
    def default_setter(self, obj, val):
        setattr(obj, self._name, val)
    
    
    def __delete__(self, obj):
        '''Deleter wrapper.'''
        if obj is None:
            return self
        if self.indelible or self.fdel is None:
            raise AttributeError(f'Property {obj.__class__.__qualname__}.{self.name} is INDELIBLE')
        self.fdel(obj)
    
    
    def default_delete(self, obj):
        if hasattr(obj, self._name):
            delattr(obj, self._name)

    def getter(self, fget):
        '''Decorator to set the Property's getter.'''
        self.fget = fget
        self.gen__doc__()
        return self
        
    def setter(self, fset):
        '''Decorator to set the Property's setter.'''
        self.fset = fset
        self.gen__doc__()
        return self
        
    def deleter(self, fdel):
        '''Decorator to set the Property's deleter.'''
        self.fdel = fdel
        self.gen__doc__()
        return self
    
    def documentor(self, fdoc):
        '''Decorator to set the Property's documentor function.'''
        self.fdoc = fdoc
        default = fdoc(self)
        if default is not None:
            self.default = default
        
        for k, v in inspect.getmembers(fdoc):
            if k == '__annotations__':
                if v is not None:
                    rt = v.get('return', None)
                    if rt is not None:
                        if isinstance(rt, type):
                            rt = (rt,)
                        if type(rt) == _UnionGenericAlias:
                            rt = rt.__args__
                        self._set_types(rt)
                        
            break;
        self.gen__doc__()
        return self
    
    
    def __call__(self, fdoc: Callable[[],Any]=None):    
        '''Alias for the documentor decorator.'''
        return self.documentor(fdoc)
    
    def gen__doc__(self):
        '''Generate the __doc__ for the Property.
        
            Documentation is compiled from the docstrings of each
            component function, as well as meta-information stored in the
            Property object, to automatically document the Property.
        '''
        def trim(docstring):
            if not docstring:
                return ''
            # Convert tabs to spaces (following the normal Python rules)
            # and split into a list of lines:
            lines = docstring.expandtabs().splitlines()
            # Determine minimum indentation (first line doesn't count):
            indent = sys.maxsize
            for line in lines[1:]:
                stripped = line.lstrip()
                if stripped:
                    indent = min(indent, len(line) - len(stripped))
            # Remove indentation (first line is special):
            trimmed = [lines[0].strip()]
            if indent < sys.maxsize:
                for line in lines[1:]:
                    trimmed.append(line[indent:].rstrip())
            # Strip off trailing and leading blank lines:
            while trimmed and not trimmed[-1]:
                trimmed.pop()
            while trimmed and not trimmed[0]:
                trimmed.pop(0)
            # Return a single string:
            return '\n'.join(trimmed)
        dget = '' if self.fget is None else getattr(self.fget, '__doc__', '')
        dset = '' if self.fset is None else getattr(self.fset, '__doc__', '')
        ddel = '' if self.fdel is None else getattr(self.fdel, '__doc__', '')
        ddoc = '' if self.fdoc is None else getattr(self.fdoc, '__doc__', '')
        docs = self.docs if isinstance(self.docs, str) else ''
        dtypes = '' if self.types is None else f'TYPE-RESTRICTED: {", ".join([getattr(t, "__qualname__", repr(t))for t in self.types])}'
        ddefault = f'default: {repr(self.default)}'
        documents = (docs, ddoc, dget, dset, ddel, dtypes, ddefault)
        self.__doc__ = '\n'.join([trim(doc) for doc in documents if isinstance(doc, str) and len(doc.strip())])

class PropertyPlus(Property):
    '''
    '''
        
    def default_validator(self, obj, val):
        isvalid = True
        return isvalid
    
    def default_type_corrector(self, obj, val):
        return val
    
    def validator(self, fval):
        '''Decorator to set the Property's validator function.'''
        if isinstance(fval, Callable):
            self.fval=fval
    
    def type_corrector(self, fval):
        '''Decorator to set the PropertyPlus' type_corrector functiun.'''
        
class SharedProperty(Property):
    '''A Property whose cache variable is shared across all instances
        of a class.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__doc__ = (f'SHARED CACHE: stored in class.\n{self.__doc__}').strip()
        
    def default_getter(self, obj):
        if not hasattr(self.owner, self._name):
            setattr(self.owner, self._name, self.default)
        return getattr(self.owner, self._name)

    def default_setter(self, obj, val):
        setattr(self.owner, self._name, val)
    
    def default_deleter(self, obj):
        if hasattr(self.owner, self._name):
            delattr(self.owner, self._name)
            
class Example:
    '''
    '''
    @Property()
    def text(self) -> str:
        '''the text of the example'''
        return ''
            
    @Property()
    def number(self) -> Union[int, float, complex]:
        '''the number of the example'''
        return 0

    @Property("A simple example with simple help.")
    def simple(self):
        return None
    
    @SharedProperty
    def shared(self) -> Optional[str]:
        '''A shared property'''
    
help(Example)
help(Property)
