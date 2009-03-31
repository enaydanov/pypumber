#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import re

def snippet(kw, pattern):
    escaped = re.escape(pattern).replace('\ ', ' ').replace('/', '\/')
    param_pattern = re.compile(r'\\"([^\"]*)"')
    escaped, n = param_pattern.subn('"([^\\"]*)"', escaped)
    arg_list = ', '.join(('arg%d' % i for i in xrange(1, n+1)))
      
    return "@%s(r'%s')\ndef _(%s):\n    pending()\n" % (kw.capitalize(), escaped, arg_list)
