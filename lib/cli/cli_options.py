#! /usr/bin/env python

from options import Options

class CommandLineOptions(Options):
    from cli_options_parser import parser

    def __init__(self, **defaults):
        Options.__init__(self, **defaults)
        self.parser.set_defaults(**defaults)
        (self.cli_opts, args) = self.parser.parse_args()

    def __getattr__(self, attr):
        if hasattr(self.cli_opts, attr):
            return getattr(self.cli_opts, attr)
        else:
            return Options.__getattr__(self, attr)
