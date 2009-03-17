#! /usr/bin/env python

import os, fnmatch, types


def find_files(paths, pattern='*', excludes=None):
    """Find files in paths with pattern.
    """
    if excludes is None:
        excludes_filter = lambda x: True
    else:
        excludes = [os.path.normpath(e) for e in excludes]
        def excludes_filter(path):
            for x in (None for e in excludes if path.find(e) != -1):
                return False
            return True

    if type(paths) == types.StringType:
        paths = (paths, )
    
    rv = []
    for path in (p for p in paths if excludes_filter(p)):
        if os.path.isfile(path):
            rv.append(os.path.abspath(path))
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if excludes_filter(os.path.join(root, d))]
            rv.extend(
                os.path.abspath(os.path.join(root, f)) 
                for f in fnmatch.filter(files, pattern) 
                if excludes_filter(os.path.join(root, f))
            )
    return set(rv)
