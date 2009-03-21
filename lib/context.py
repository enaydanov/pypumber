#! /usr/bin/env python

from cfg.set_defaults import set_defaults

class Context(object):
    def __init__(self, reporter):
        set_defaults(self, 'strict')
        self.reporter = reporter
        self._call_stack = []
    
    def _register_call(self, attr, *args, **kwargs):
        self._call_stack.append((attr, args, kwargs))
        return self
    
    def __getattr__(self, attr):
        if attr.startswith('skip_'):
            if hasattr(self.reporter, attr):
                return getattr(self.reporter, attr)
            return lambda *args, **kwargs: None
        return lambda *args, **kwargs: self._register_call(attr, *args, **kwargs)
    
    def __enter__(self):
        if self._call_stack:
            attr, args, kwargs = self._call_stack[-1]
            attr = 'start_%s' % attr
            if hasattr(self.reporter, attr):
                getattr(self.reporter, attr)(*args, **kwargs)
    
    def __exit__(self, type, value, traceback):
        if self._call_stack:
            attr, _, _= self._call_stack.pop()
            if type is None:
                # All fine. Just call pass function.
                attr = 'pass_%s' % attr
                if hasattr(self.reporter, attr):
                    getattr(self.reporter, attr)()
            else:
                attr = 'fail_%s' % attr
                if hasattr(self.reporter, attr):
                    getattr(self.reporter, attr)(type, value, traceback)
                if self.strict:
                    return False
            return True
