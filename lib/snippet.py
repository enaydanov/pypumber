#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import re, types

def snippet(kw, pattern, multi=None):
    escaped = re.escape(pattern).replace('\ ', ' ').replace('/', '\/')
    param_pattern = re.compile(r'\\"([^\"]*)"')
    escaped, n = param_pattern.subn('"([^\\"]*)"', escaped)
    arg_list = ['arg%d' % i for i in xrange(1, n+1)]
    
    multi_param = ''
    comment = ''
    
    if multi is not None:
        if type(multi) == types.StringType:
            multi_param = ', string=multi'
            arg_list.append('string')
            comment = '    # string is a pypumber.PyString\n'
        else:
            multi_param = ', table=multi'
            arg_list.append('table')
            comment = '    # table is a pypumber.Table\n'
    
    return "@%s(r'%s'%s)\ndef _(%s):\n%s    pending()\n" % (kw.capitalize(), escaped, multi_param, ', '.join(arg_list), comment)
