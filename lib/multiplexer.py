#! /usr/bin/env python

"""Multiplexer for attributes lookup, calls, etc.

Example:
    >>> lst1 = [1]
    >>> lst2 = [2]
    >>> m = Multiplexer(lst1, lst2)
    >>> m.append(2)     # There is multiplexing of lookup 'append' 
                                # attribute and of calling it with arg '2'
    
    >>> lst1
    [1, 2]
    
    >>> lst2
    [2, 2]
"""

class _Outputs(list):
    """Class for representing list of Multiplexer output objects
    """
    def __init__(self, multiplexer):
        list.__setattr__(self, '__multiplexer',  multiplexer)
        
    def __getattribute__(self, attr):
        return lambda *args, **kwargs: \
            getattr(list, attr)(list.__getattribute__(self, '__multiplexer'), *args, **kwargs) 

    def __len__(self):
        return self.__len__()

    def __getitem__(self, key):
        return self.__getitem__(key)
    
    def __setitem__(self, key, value):
        self.__setitem__(key, value)
    
    def __delitem__(self, key):
        self.__delitem__(key)
    
    def __getslice__(self, i, j):
        return self.__getslice__(i, j)
    
    def __setslice__(self, i, j, sequence):
        self.__setslice__(i, j, sequence)

    def __iter__(self):
        return self.__iter__()
    
    def __contains__(self, value):
        return self.__contains__(value)


class Multiplexer(list):
    def __init__(self, *objs):
        append = getattr(list, 'append')
        for obj in objs:
            append(self, obj)
        list.__setattr__(self, '__outputs__', _Outputs(self))
    
    def __getattribute__(self, attr):
        if attr == '__outputs__':
            return list.__getattribute__(self, attr)
        raise AttributeError
    
    def __getattr__(self, attr):
        return Multiplexer(*[getattr(obj, attr) for obj in self])

    def __setattr__(self, attr, value):
        for obj in self:
            setattr(obj, attr, value)
    
    def __delattr__(self, attr):
        for obj in self:
            delattr(obj, attr)

    def __getitem__(self, key):
        return Multiplexer(*[obj[key] for obj in self])

    def __setitem__(self, key, value):
        for obj in self:
            obj[key] = value
    
    def __delitem__(self, key):
        for obj in self:
            del(obj[key])
        
    def __getslice__(self, i, j):
        return Multiplexer(*[obj[i:j] for obj in self])
    
    def __setslice__(self, i, j, sequence):
        for obj in self:
            obj[i:j] = sequence
        
    def __call__(self, *args, **kwargs):
        return Multiplexer(*[obj(*args, **kwargs) for obj in self])
