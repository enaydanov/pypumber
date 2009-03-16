#! /usr/bin/env python

"""Supplimentary class for handling options from different sources.

Example:
    1) define subclass which really set options:
        >>> class OptionsFromSomewhere(Options):
        >>>    def __init__(self):
        >>>       Options.__init__(self)
        >>>       self.options = read_options_from_somewhere()
    
    2) make instance:
        >>> opts = OptionsFromSomewhere()

    3) apply options to object that need to be configured:
        >>> opts(real_object_to_be_configured)
"""

import types

class Options(object):
    def __init__(self, **options):
        self.options = options
        self.AccumulatorType = types.ListType
    
    def __getattr__(self, attr):
        if attr in self.options:
            return self.options[attr]
        raise AttributeError("A instance has no attribute '%s'" % attr)
    
    def __call__(self, *objs):
        """Apply options to given objects.
        
        Go thru self.options and if object have such attr try to update it:
            1) if attr is a instance of self.AccumulatorType then append or extend;
            2) just set attr in other case.
        """
        for obj in objs:
            for opt, value in ((k, v) for k, v in self.options.items() if hasattr(obj, k) and v is not None):
                obj_opt = getattr(obj, opt)
                if type(obj_opt) == self.AccumulatorType:
                    if type(value) in [types.ListType, self.AccumulatorType]:
                        obj_opt.extend(value)
                    else:
                        obj_opt.append(value)
                else:
                    setattr(obj, opt, value)
