#! /usr/bin/env python

_accum_attrs = ['scenario_names', 'path', 'excludes', 'require']
_single_value_attrs = ['tags', 'strict', 'autoformat', 'backtrace', 
    'dry_run', 'guess', 'verbose', 'color', 'multiline', 'source', 
    'snippets']

def set_defaults(obj, *attrs):
    for attr in attrs:
        if attr in _accum_attrs:
            value = []
        elif attr in _single_value_attrs:
            value = None
        else:
            raise AttributeError("Error: unknown option: '%s'" % attr)
        setattr(obj, attr, value)
