#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import sys, os.path, types, traceback, string, collections

from cfg.set_defaults import set_defaults
from reporter import Reporter
from colors import ColoredOutput, highlight_groups
from snippet import snippet
from step_definitions import Undefined

class ProgressReporter(Reporter):
    def __init__(self):
        set_defaults(self, 'backtrace', 'color_scheme', 'source', 'multiline', 'snippets', 'strict')
        self.__out = ColoredOutput(sys.stdout)

        # Statistics.
        self.counts = collections.defaultdict(int)

        # Set of undefined steps.
        self.undefined = dict()
        
        self.chars = {
            'passed': self.color_scheme.passed('.'),
            'failed': self.color_scheme.failed('F'),
            'undefined': self.color_scheme.undefined('U'),
            'pending': self.color_scheme.pending('P'),
            'skipped': self.color_scheme.skipped('-'),
        }


    # 'color' property
    def get_color(self):
        return not self.__out.skip_colors
    def set_color(self, value):
        self.__out.skip_colors = not value
    color = property(get_color, set_color)

    # 'out' property
    def get_out(self):
        return self.__out
    def set_out(self, stream):
        self.__out.output_stream = stream 
    out = property(get_out, set_out)


    def print_snippets(self):
        if self.undefined:
            formatted = ["\nYou can implement step definitions for missing steps with these snippets:\n", ]
            for name, (kw, multi) in self.undefined.items():
                formatted.append('\n')
                formatted.append(snippet(kw, name, multi))
            self.__out.write(self.color_scheme.undefined(''.join(formatted)))


    def run(self, run):
        if run.status is None:
            return

        formatted = ['\n']
        formatted.append('%d scenario%s\n' % (self.counts['scenarios'], 's' if self.counts['scenarios'] != 1 else ''))
        for s in ['failed', 'skipped', 'undefined', 'pending', 'passed', ]:
            if self.counts[s]:
                formatted.append(getattr(self.color_scheme, s)(
                    '%d %s step%s\n' % (self.counts[s], s, self.counts[s] != 1 and 's' or '')
                ))
        self.__out.write(''.join(formatted))
        
        self.print_snippets()


    def step(self, step):
        if step.status is None:
            return
            
        self.counts[step.status] += 1

        if self.snippets and step.status == 'undefined' and step.name not in self.undefined:
            self.undefined[step.name] = (step.section, step.multi)
        
        if step.status in self.chars:
            self.__out.write(self.chars[self.status])
