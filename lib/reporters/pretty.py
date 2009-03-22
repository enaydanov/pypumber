#! /usr/bin/env python

import sys, os.path, inspect

from cfg.set_defaults import set_defaults
from reporter import Reporter
from colors import ColoredOutput, highlight_groups
from step_definitions import MatchNotFound


class Step(object):
    def __init__(self, section, kw, i18n_kw, name, source_indent, matchobj=None, fn=None):
        self.section, self.kw, self.i18n_kw, self.name, self.source_indent, self.matchobj, self.fn = section, kw, i18n_kw, name, source_indent, matchobj, fn


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

    def pass_run(self):
        formatted = ['\n']
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
    #~ def skip_feature(self, filename, header, tags):
        #~ pass
        
    def start_feature(self, filename, header, tags):
        header = header.split('\n', 1)
        formatted = [header[0]]
        if self.source:
            formatted.append('  ')
            formatted.append(self.color_scheme.comment('# ' + os.path.relpath(filename)))
        formatted.extend(['\n', header[1], '\n'])
        with self.__out as out:
            out.write(''.join(formatted))

    #~ def pass_feature(self):
        #~ pass
    
    #~ def fail_feature(self, type, value, traceback):
        #~ pass


    # Handlers for reporting of steps execution.
    #~ def start_background(self, i18n_kw):
        #~ pass

    #~ def pass_background(self):
        #~ pass
    
    #~ def fail_background(self, type, value, traceback):
        #~ pass

    # Handlers for reporting of steps execution.
    #~ def skip_scenario(self, kw, i18n_kw, name, tags):
        #~ pass
    
    def start_scenario(self, kw, i18n_kw, name, tags):
        formatted = [' ' * self.scenario_indent, self.color_scheme.passed(i18n_kw + ' ' + name)]
        formatted.append('\n')
        with self.__out as out:
            out.write(''.join(formatted))
        self.counts['scenarios'] += 1

    def pass_scenario(self):
        self.__out.write('\n')
    
    def fail_scenario(self, type, value, traceback):
        self.pass_scenario()

    # Handlers for reporting of steps execution.
    def start_step(self, section, kw, i18n_kw, name, source_indent):
        self.last_step = Step(section, kw, i18n_kw, name, source_indent)
        return self.last_step
    
    def pass_step(self):
        formatted = [' ' * self.step_indent, self.color_scheme.passed(self.last_step.i18n_kw), ' ']
        formatted.append(highlight_groups(
            self.last_step.matchobj, 
            self.color_scheme.passed, 
            self.color_scheme.passed_param
        ))
        if self.source:
            formatted.append(' ' * self.last_step.source_indent)
            formatted.append(self.color_scheme.comment(
                '# %s:%d' % (os.path.relpath(inspect.getfile(self.last_step.fn)), inspect.getsourcelines(self.last_step.fn)[1])
            ))
        formatted.append('\n')
        
        with self.__out as out:
            out.write(''.join(formatted))
        self.counts['passed'] += 1
    
    def fail_step(self, type, value, traceback):
        formatted = [' ' * self.step_indent]
        if issubclass(type, MatchNotFound):
            formatted.append(self.color_scheme.undefined(self.last_step.i18n_kw + ' ' + self.last_step.name))
            self.counts['pending'] += 1
        else:
            formatted.append(highlight_groups(
                self.last_step.matchobj, 
                self.color_scheme.failed, 
                self.color_scheme.failed_param
            ))
        formatted.append('\n')
    
        with self.__out as out:
            out.write(''.join(formatted))
        
        self.counts['failed'] += 1
