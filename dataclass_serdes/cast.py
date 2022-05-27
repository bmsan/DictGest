import copy
from multiprocessing.sharedctypes import Value
from typing import Any, Callable, Iterable, Mapping, types

from numpy import isin

class Convertor:
    def __init__(self):
        self.mappings = {}
    
    def register(self, dtype: type, converter: Callable):
        self.mappings[dtype] = converter
    
    def convert(self, data, dtype: type):
        if dtype in self.mappings:
            return self.mappings[dtype](data)
        
        return convert(data, dtype)
 
def convert_mapping(data, dtype, mappings):
    origin = dtype.__origin__
    if not issubclass(origin, Mapping):
        raise ValueError()
    
    args = dtype.__args__
    assert len(args) == 2
    assert isinstance(data, Mapping)
    # Here we should actually try to create the mapping type
    # 1. Try to create the Mapping datatype
    # 2. If above fails try to copy if the original data is the desired datatype
    # 3. Fallback to dictionary
    try:
        res = origin()
    except Exception as e:
        if  isinstance(data, origin):
            res = copy.copy(data)
        else:
            #TODO: Raise warning  
            #TODO: Maybe look at default value  
            res = {}
    key_type, val_type = args
    for key, val in data.items():
        key = convert(key, key_type, mappings)
        val = convert(val, val_type, mappings)
        res[key] = val
    return res 


def convert_iterable(data, dtype, mappings):
    origin = dtype.__origin__
    if not issubclass(origin, Iterable):
        raise ValueError()
    
    args = dtype.__args__
    
    
    elements = []
    if len(args) == 1:
        for el in data:
            elements.append(convert(el, args[0], mappings))
    else:
        assert len(args) == len(data)
        for dt_val, el in zip(args, data):
           elements.append(convert(el, dt_val, mappings))

    res = origin(elements)
    
    return res 



def convert(data: Any, dtype: types.GenericAlias, mappings: dict[type, Callable]=None):
    if type(dtype) == type and isinstance(data, dtype):
        return data
    if mappings and dtype in mappings:
        return mappings[dtype](data)
    if type(dtype) == type: # base type
        return dtype(data)
    elif type(dtype) == types.GenericAlias:
        origin = dtype.__origin__
        if issubclass(origin, Mapping):
            return convert_mapping(data, dtype, mappings)
        elif issubclass(origin, Iterable):
            return convert_iterable(data, dtype, mappings)

if __name__ == '__main__':
    r = convert(3.4, float)
    print(r, type(r))
    
    r = convert('3.4', float)
    print(r, type(r))
    r = convert(3.4, int)
    print(r, type(r))
 
    r = convert([3.4, '7', '8'], list[int])
    print(r, type(r))
  
  
    r = convert([3.4, '7', '8'], tuple[float, str, int])
    print(r, type(r))
  
    r = convert([3.4, '7', '8'], set[str])
    print(r, type(r))
  
    r = convert([   
                 (1,2,3,'4'), 
                 ('3.4', '5', 7.6, 9.2), 
                 (('a', 'bc', 'de'), ['a', 'a', 'b', 'a'])
                ], tuple[list[int], set[float], list[set[str]]])
    print(r, type(r))
   
    r = convert({'aa' : '3.4', 4 : 6.5, 'bb': '1'}, dict[str, float])
    print(r, type(r))
        
    r = convert({'aa' : ['3.4'], 4 : [6.5], 'bb': ['1']}, dict[str,tuple])
    print(r, type(r))
   
    r = convert({'aa' : ['3.4'], 4 : [6.5], 'bb': ['1']}, dict[str,tuple[float]])
    print(r, type(r))
 
    r = convert({'aa' : ['3.4'], 4 : [6.5], 'bb': ['1']}, dict)
    print(r, type(r))
          
# convert(None, list[int])
# convert(None, list[tuple[dict[str, float]]])
# convert(None, dict[tuple[dict[str, float]]])