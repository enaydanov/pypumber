#! /usr/bin/env python

import sys, os.path, types, traceback, string

from cfg.set_defaults import set_defaults
from reporter import Reporter
from colors import ColoredOutput, highlight_groups


class StepContext(object):
    def __init__(self, section, step, matchobj=None, source_file=None, source_line=None):
        self.section, self.step, self.matchobj, self.source_file, self.source_line = section, step, matchobj, source_file, source_line


class PrettyReporter(Reporter):
    def __init__(self):
        set_defaults(self, 'backtrace', 'color_scheme', 'source', 'multiline', 'backtrace')
        self.__out = ColoredOutput(sys.stdout)
        self.counts = {
            'scenarios': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'pending': 0,
            'undefined': 0,
        }
        self.scenario_indent = 2
        self.step_indent = 4
        self.source_indent = 0
        self.table_indent = 6
        self.talign = string.ljust
        self.traceback_indent = 6
        self.filename = None
        self.silent_steps = False
        self.background_shown = False
        self.feature_header = None
    
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
    
    # Handlers for reporting about whole run execution.
    #~ def start_run(self, scenario_names, tags):
        #~ pass

    def set_source_indent(self, steps, minimal):
        lengths = [len(step.kw_i18n) + len(step.name) for step in steps]
        lengths.append(self.scenario_indent - self.step_indent + minimal)
        self.source_indent = max(lengths) + 2

    def end_run(self):
        formatted = []
        formatted.append('%d scenario%s\n' % (self.counts['scenarios'], 's' if self.counts['scenarios'] != 1 else ''))
        for s in ['failed', 'skipped', 'undefined', 'pending', 'passed', ]:
            if self.counts[s]:
                formatted.append(getattr(self.color_scheme, s)(
                    '%d step%s %s\n' % (self.counts[s], 's' if self.counts[s] != 1 else '', s)
                ))
        self.__out.write(''.join(formatted))
    
    # Handlers for reporting of feature execution.
    #~ def skip_feature(self, filename, feature):
        #~ pass
        
    def start_feature(self, filename, feature):
        formatted, self.filename, header, tags = [], filename, feature.header.split('\n', 1), feature.tags()
        
        # Print tags.
        if tags:
            formatted.extend((self.color_scheme.tag(' '.join(tags)), '\n'))
        
        # Print first line of header.
        formatted.append(header[0])
        
        # Print source of feature as part of first line.
        if self.source:
            formatted.extend(('  ', self.color_scheme.comment('# ' + os.path.relpath(filename))))
        
        formatted.append('\n')
        
        # Print rest of header.
        if len(header) == 2:
            formatted.extend((header[1], '\n'))
        
        formatted.append('\n')
        
        # Deferring output.
        self.feature_header = ''.join(formatted)

    def show_feature_header(self):
        if self.feature_header is not None:
            self.__out.write(self.feature_header)
            self.feature_header = None

    def end_feature(self):
        if self.feature_header is None:
            self.__out.write('\n')
        self.feature_header = None

    # Handlers for reporting of steps execution.
    def start_background(self, bg):
        if self.background_shown:
            self.silent_steps = True
            return
        
        self.show_feature_header()
        
        self.__out.write(''.join(
            (' ' * self.scenario_indent, self.color_scheme.passed(bg.kw_i18n), '\n')
        ))

    def end_background(self):
        self.silent_steps = False
        
        if self.background_shown:
            return
        
        self.__out.write('\n')
        self.background_shown = True
        

    # Handlers for reporting of steps execution.
    #~ def skip_scenario(self, scenario):
        #~ pass
    
    def start_scenario(self, sc):
        self.show_feature_header()
        
        formatted, indent, tags = [], ' ' * self.scenario_indent, sc.tags()
        kw, name, lineno = sc.kw_i18n, sc.name, sc.lineno
        
        # Print tags.
        if tags:
            formatted.extend((indent, self.color_scheme.tag(' '.join(tags)), '\n'))

        # Calculate source indent for this scenario. 
        sc_len = len(kw) + len(name)
        self.set_source_indent(sc.steps, sc_len)
        
        # Print Scenario line.
        formatted.extend((indent, self.color_scheme.passed('%s %s' % (kw, name))))
        
        # Print source of scenario.
        if self.source:
            formatted.append(' ' * (self.source_indent - sc_len + self.step_indent - self.scenario_indent))
            formatted.append(self.color_scheme.comment(
                '# %s:%d' % (os.path.relpath(self.filename), lineno)
            ))
        
        formatted.append('\n')
        
        self.__out.write(''.join(formatted))
        self.counts['scenarios'] += 1

    def end_scenario(self):
        self.__out.write('\n')

    # Handlers for reporting of steps execution.
    def start_step(self, section, step):
        self.last_step = StepContext(section, step)
    
    def step_definition(self, match):
        self.last_step.matchobj = match.matchobj
        self.last_step.source_file = match.source_file
        self.last_step.source_line = match.source_line
    
    def format_last_step(self, regular, highlight=None):
        if self.silent_steps:
            return
        
        step = self.last_step.step
        
        kw, name, multi, indent = step.kw_i18n, step.name, step.multi, ' ' * self.step_indent
           
        formatted = [indent, regular(kw), ' ']
        formatted.append(
            regular(name) 
                if highlight is None else 
            highlight_groups(
                self.last_step.matchobj, 
                regular, 
                highlight
            )
        )
        
        # Print source of steps and scenarios.
        if self.source:
            source_file = self.last_step.source_file
            source_line = self.last_step.source_line
            if source_file is None or source_line is None:
                source_file = self.filename
                source_line = step.lineno 
            formatted.append(' ' * (self.source_indent - len(kw) - len(name)))
            formatted.append(self.color_scheme.comment(
                '# %s:%d' % (os.path.relpath(source_file), source_line)
            ))
        formatted.append('\n')
        
        # Print mulitiline args.
        if self.multiline and multi is not None:
            if type(multi) == types.StringType:
                # PyString
                formatted.append(regular(
                    '%s"""\n%s\n%s"""\n' % (indent, multi, indent)
                ))
            else:
                # Table
                fields, rows, w = multi[0], multi[1:], {}
                
                # Calculate columns width.
                for f in fields:
                    w[f] = max(len(f), max(len(row[f]) for row in rows))
                
                # Table row prefix.
                row_start = ' ' * self.table_indent + '| '
                
                # Print table.
                table = [row_start, ' | '.join(self.talign(f, w[f]) for f in fields), ' |\n']
                for row in rows:
                    table.extend(
                        (row_start, ' | '.join(self.talign(row[f], w[f]) for f in fields), ' |\n')
                    )                
                formatted.append(regular(''.join(table)))
        
        self.__out.write(''.join(formatted))
    
    def pass_step(self):
        self.format_last_step(self.color_scheme.passed, self.color_scheme.passed_param)
        self.counts['passed'] += 1

    def undefined_step(self):
        self.format_last_step(self.color_scheme.undefined)
        self.counts['undefined'] += 1

    def skip_step(self):
        self.format_last_step(self.color_scheme.skipped, self.color_scheme.skipped_param)
        self.counts['skipped'] += 1

    def fail_step(self, exc):
        self.format_last_step(self.color_scheme.failed, self.color_scheme.failed_param)
        if self.backtrace:
            indent = ' ' * self.traceback_indent
            exc_str = []
            for line in traceback.format_exc().split('\n'):
                exc_str.append(indent + line)
            self.__out.write(self.color_scheme.failed('\n'.join(exc_str)))
            self.__out.write('\n')
        self.counts['failed'] += 1

    def pending_step(self):
        self.format_last_step(self.color_scheme.pending, self.color_scheme.pending_param)
        self.counts['pending'] += 1
