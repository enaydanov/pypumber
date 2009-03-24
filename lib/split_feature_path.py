#! /usr/bin/env python

import re, os.path

_FEATURE_FILE_RE = re.compile(r'(?P<filename>.*\.feature)(?P<line_numbers>(:(\d+))*)$')

def split_feature_path(path):
    match = _FEATURE_FILE_RE.match(path)
    if match is not None:
        (feature, lines) = match.group('filename', 'line_numbers')
        if os.path.isfile(feature):
            return feature,  [int(n) for n in lines.split(':')[1:]]
    return path, None
