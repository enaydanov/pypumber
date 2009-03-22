#! /usr/bin/env python

import sys, os.path, inspect

from cfg.set_defaults import set_defaults
from reporter import Reporter
from colors import ColoredOutput, highlight_groups
from step_definitions import MatchNotFound
from run import SkipStep


class StepContext(object):
    def __init__(self, section, step, matchobj=None, fn=None):
        self.section, self.step, self.matchobj, self.fn = section, step, matchobj, fn


class PrettyReporter(Reporter):
    def __init__(self):
        set_defaults(self, 'backtrace', 'color_scheme', 'source')
        self.__out = ColoredOutput(sys.stdout)
        self.counts = {
            'scenarios': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'pending': 0,
        }
        self.scenario_indent = 2
        self.step_indent = 4
        self.source_indent = 0
        self.filename = None
        
    @property
    def color(self):
        return not self.__out.skip_colors
    
    @color.setter
    def color(self, value):
        self.__out.skip_colors = not value
    
    @property
    def out(self):
        return self.__out
    
    @out.setter
    def out(self, stream):
        self.__out.output_stream = stream 
    
    # Handlers for reporting about whole run execution.
    #~ def start_run(self, scenario_names, tags):
        #~ pass

    def set_source_indent(self, steps, minimal):
        lengths = [len(step['step_keyword'][1]) + len(step['name']) for step in steps]
        lengths.append(minimal)
        self.source_indent = max(lengths) + 2

    def pass_run(self):
        formatted = []
        formatted.append('%d scenario%s\n' % (self.counts['scenarios'], 's' if self.counts['scenarios'] != 1 else ''))
        for s in ['passed', 'failed', 'skipped', 'pending']:
            if self.counts[s]:
                formatted.append(getattr(self.color_scheme, s)(
                    '%d step%s %s\n' % (self.counts[s], 's' if self.counts[s] != 1 else '', s)
                ))
        with self.__out as out:
            out.write(''.join(formatted))
    
    def fail_run(self, type, value, traceback):
        self.pass_run()

    # Handlers for reporting of feature execution.
    #~ def skip_feature(self, filename, feature):
        #~ pass
        
    def start_feature(self, filename, feature):
        # TODO: print tags
        self.filename = filename
        header = feature.header.split('\n', 1)
        formatted = [header[0]]
        if self.source:
            formatted.append('  ')
            formatted.append(self.color_scheme.comment('# ' + os.path.relpath(filename)))
        formatted.append('\n')
        if len(header) == 2:
            formatted.append(header[1])
            formatted.append('\n')
        with self.__out as out:
            out.write(''.join(formatted))

    def pass_feature(self):
        self.__out.write('\n')
    
    def fail_feature(self, type, value, traceback):
        self.pass_feature()


    # Handlers for reporting of steps execution.
    #~ def start_background(self, background):
        #~ pass

    #~ def pass_background(self):
        #~ pass
    
    #~ def fail_background(self, type, value, traceback):
        #~ pass

    # Handlers for reporting of steps execution.
    #~ def skip_scenario(self, scenario):
        #~ pass
    
    def start_scenario(self, scenario):
        str_len = len(scenario[1].scenario_keyword[0]) + len(scenario[1].name)
        self.set_source_indent(scenario[1].steps, str_len)
        formatted = [
            ' ' * self.scenario_indent, 
            self.color_scheme.passed('%s %s' % (scenario[1].scenario_keyword[0], scenario[1].name)),
        ]
        if self.source:
            formatted.append(' ' * (self.source_indent - str_len + self.step_indent - self.scenario_indent))
            formatted.append(self.color_scheme.comment(
                '# %s:%d' % (os.path.relpath(self.filename), scenario[1].scenario_keyword[1])
            ))
        formatted.append('\n')
        with self.__out as out:
            out.write(''.join(formatted))
        self.counts['scenarios'] += 1

    def pass_scenario(self):
        self.__out.write('\n')
    
    def fail_scenario(self, type, value, traceback):
        self.pass_scenario()

    # Handlers for reporting of steps execution.
    def start_step(self, section, step):
        self.last_step = StepContext(section, step)
        return self.last_step
    
    def format_last_step(self, regular, highlight=None):
        kw = self.last_step.step.step_keyword[1]
        lineno = self.last_step.step.step_keyword[2]
        fn = self.last_step.fn
        name = self.last_step.step.name
        
        formatted = [' ' * self.step_indent, regular(kw), ' ']
        formatted.append(
            regular(name) 
                if highlight is None else 
            highlight_groups(
                self.last_step.matchobj, 
                regular, 
                highlight
            )
        )
        if self.source:
            if fn is None:
                file_line = (os.path.relpath(self.filename), lineno)
            else:
                file_line = (os.path.relpath(inspect.getfile(fn)), inspect.getsourcelines(fn)[1])
            formatted.append(' ' * (self.source_indent - len(kw) - len(name)))
            formatted.append(self.color_scheme.comment(
                '# %s:%d' % file_line
            ))
        formatted.append('\n')
        
        with self.__out as out:
            out.write(''.join(formatted))
    
    def pass_step(self):
        self.format_last_step(self.color_scheme.passed, self.color_scheme.passed_param)
        self.counts['passed'] += 1
    
    def fail_step(self, type, value, traceback):
        if issubclass(type, SkipStep):
            self.format_last_step(self.color_scheme.skipped, self.color_scheme.skipped_param)
            self.counts['skipped'] += 1
        elif issubclass(type, MatchNotFound):
            self.format_last_step(self.color_scheme.undefined)
            self.counts['pending'] += 1
        else:
            self.format_last_step(self.color_scheme.failed, self.color_scheme.failed_param)
            self.counts['failed'] += 1
