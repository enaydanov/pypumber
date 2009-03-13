#! /usr/lib/env python

import types

def _buildNode(obj):
    if type(obj) == types.DictType:
        return _NodeMap(obj)
    elif type(obj) in (types.ListType, types.TupleType):
        return _NodeCollection(obj)
    return obj

	
Node = _buildNode


class _Node(object):
    def __init__(self, obj):
        self.__obj = obj
    
    def __call__(self):
        return self.__obj

    def __contains__(self, key):
        return key in self.__obj

    def __getitem__(self, key):
        return Node(self.__obj[key])

		
class _NodeMap(_Node):
    def __getattr__(self, attr):
        try:
            attr = self()[attr]
        except KeyError:
            raise AttributeError
        return Node(attr)

    def __iter__(self):
        return (k for k in self())


class _NodeCollection(_Node):
    def __iter__(self):
        return (Node(v) for v in self())


if __name__ == '__main__':
    pass
