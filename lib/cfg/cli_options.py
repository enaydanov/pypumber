#! /usr/bin/env python

import os.path

from options import Options

class CommandLineOptions(Options):
    def __init__(self):
        from cli_options_parser import parser
        
        Options.__init__(self)
        opts, args = parser.parse_args()
        self.options = opts.__dict__
        self.options['path'] = [os.path.normpath(path) for path in args]
