#! /usr/bin/env python

def subst_params(str, pattern, values):
    """Substitute parameters due to given regexp.
    
    str -- string template
    pattern -- compiled regexp
    values -- dict with actual values
    """
    subst = False
    chunks = []
    used = set()
    for chunk in pattern.split(str):
        if subst:
            used.add(chunk)
            chunk = values[chunk]
        chunks.append(chunk)
        subst = not subst
    return ''.join(chunks), used
