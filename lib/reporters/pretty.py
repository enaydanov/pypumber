#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import sys, os.path, types, traceback, string, collections
from StringIO import StringIO

from cfg.set_defaults import set_defaults
from reporter import Reporter
from colors import ColoredOutput, highlight_groups
from snippet import snippet
from step_definitions import Undefined


class PrettyReporter(Reporter):
    def __init__(self):
        set_defaults(self, 'backtrace', 'color_scheme', 'source', 'multiline', 'snippets', 'strict')
        self.__out = ColoredOutput(sys.stdout)
        self.__real_out = self.__out

        self.silent_steps = False
        self.current_feature = None
        self.talign = string.ljust

        # Indents.
        self.scenario_indent = 2
        self.step_indent = 4
        self.multiline_indent = 6
        self.traceback_indent = 6
        self.source_indent = 0  # will be recalculated for each scenario

        # Statistics.
        self.counts = collections.defaultdict(int)
        
        # Deferred output.
        self.feature_header = None
        self.scenario_outline_header = None

        # Scenario formatter by default.
        self.scenario = self.__default_scenario_formatter
        
        # Set of undefined steps.
        self.undefined = dict()

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
        self.__real_out = self.__out
    out = property(get_out, set_out)

    #
    # Format helpers.
    # 

    def set_source_indent(self, steps, minimal):
        lengths = [self.scenario_indent - self.step_indent + minimal,]
        if steps is not None:
            lengths.extend([len(self.format_name(step.kw_i18n, step.name)) for step in steps])
        self.source_indent = max(lengths)


    def format_tags(self, tags):
        return self.color_scheme.tag(' '.join(tags))


    def format_source(self, filename, lineno=None, indent=1):
        source = ['# ',  os.path.relpath(filename),]
        if lineno is not None:
            source.append(':%d' % lineno)
        
        return ''.join([' ' * indent, self.color_scheme.comment(''.join(source))])


    def format_table_row(self, cols):
        rv = ['']
        for value, color, width in cols:
            rv.append(color(' %s ' % self.talign(value, width)))
        rv.append('')
        
        return '|'.join(rv)
    
    
    def format_name(self, kw, name):
        from gherkin.i18n_grammar import _language
        
        return '%s%s%s' % (kw, _language.space_after_keyword and ' ' or '', name)


    def print_feature_header(self):
        if self.feature_header is not None:
            self.__out.write(self.feature_header)
            self.feature_header = None


    def print_scenario_outline_header(self):
        if self.scenario_outline_header is not None:
            self.__out.write(self.scenario_outline_header)
            self.scenario_outline_header = None
        

    def print_exception(self, exception, tb, status):
        if self.backtrace and tb:
            error_message = traceback.format_exception(type(exception), exception, tb)
        else:
            error_message = traceback.format_exception_only(type(exception), exception)
        error_message = ''.join(error_message).split('\n')
        indent = ' ' * self.traceback_indent
        formatted = []
        for line in error_message:
            formatted.extend((indent + line, '\n'))

        self.__out.write(getattr(self.color_scheme, status, lambda x: x)(''.join(formatted)))


    def print_snippets(self):
        if self.undefined:
            formatted = ["\nYou can implement step definitions for missing steps with these snippets:\n", ]
            for name, (kw, multi) in self.undefined.items():
                formatted.append('\n')
                formatted.append(snippet(kw, name, multi))
            self.__out.write(self.color_scheme.undefined(''.join(formatted)))

    #
    # Handlers for events.
    #

    def run(self, run):
        if run.status is None:
            return

        formatted = []
        formatted.append('%d scenario%s\n' % (self.counts['scenarios'], 's' if self.counts['scenarios'] != 1 else ''))
        for s in ['failed', 'skipped', 'undefined', 'pending', 'passed', ]:
            if self.counts[s]:
                formatted.append(getattr(self.color_scheme, s)(
                    '%d %s step%s\n' % (self.counts[s], s, self.counts[s] != 1 and 's' or '')
                ))
        self.__out.write(''.join(formatted))
        
        self.print_snippets()


    def feature(self, feature):
        if feature.status == 'done':
            self.current_feature = None
            if self.feature_header is None:
                self.__out.write('\n')
            self.feature_header = None
            return
        
        self.current_feature = feature
        
        header = feature.header.split('\n', 1)
        
        formatted = []
        
        # Print tags.
        if feature.tags:
            formatted.append(self.format_tags(feature.tags))
            formatted.append('\n')
        
        # Print first line of header.
        formatted.append(header[0])
        
        # Print source of feature as part of first line.
        if self.source:
            formatted.append(self.format_source(feature.filename))
        
        formatted.append('\n')
        
        # Print rest of header.
        if len(header) == 2:
            formatted.extend((header[1], '\n'))
        
        # Deferring output.
        self.feature_header = ''.join(formatted)


    def __default_scenario_formatter(self, sc):
        if sc.status is not None:
            self.counts['scenarios'] += 1
            return
        
        self.print_feature_header()
        
        formatted = ['\n']
        indent = ' ' * self.scenario_indent
        
        kw, name = sc.kw_i18n, sc.name
        
        # Print tags.
        if sc.tags:
            formatted.extend((indent, self.format_tags(sc.tags), '\n'))

        # Calculate source indent for this scenario. 
        sc_len = len(kw) + len(name) + 1
        self.set_source_indent(sc.steps, sc_len)
        
        # Print Scenario line.
        formatted.extend((indent, '%s %s' % (kw, name)))
        
        # Print source of scenario.
        if self.source:
            formatted.append(self.format_source(
                self.current_feature.filename,
                sc.lineno,
                self.source_indent - sc_len + self.step_indent - self.scenario_indent + 1
            ))
        
        formatted.append('\n')
        
        self.__out.write(''.join(formatted))
                
        self.silent_steps = False


    def __outline_scenario_formatter(self, sc):
        if sc.status is None:
            self.print_scenario_outline_header()
            self.silent_steps = True
            return
        
        # Collect colors for cells
        params_status = collections.defaultdict(lambda: '')
        for step in sc.steps:
            for param in step.used_parameters:
                params_status[param] = step.status

        row = [(
            sc.current_row[f], 
            getattr(self.color_scheme, params_status[f], lambda x: x), 
            sc.current_widths[f]
        ) for f in sc.current_columns]
        
        self.__out.write(''.join((' '* self.step_indent, self.format_table_row(row), '\n',)))
        
        if sc.exception and (self.strict or not isinstance(sc.exception, Undefined)):
            self.print_exception(sc.exception, sc.tb, sc.status)

        # Statistics.
        self.counts['scenarios'] += 1


    def scenario_outline(self, sc):
        if sc.status == 'done':
            self.print_scenario_outline_header()
            self.counts['scenarios'] -= 1
            self.scenario = self.__default_scenario_formatter
        else:
            self.print_feature_header()
            self.__out = StringIO()
            sc.run(None)


    def examples(self, ex):
        formatted = ['\n', ' ' * self.scenario_indent, ex.kw_i18n, ' ', ex.name, '\n', ' ' * self.step_indent]
        formatted.append(self.format_table_row(zip(
            ex.table.columns,
            (self.color_scheme.outline_param, ) * len(ex.table.columns),
            (ex.table.widths[f] for f in ex.table.columns)
        )))
        formatted.append('\n')
        self.__out.write(''.join(formatted))
        self.scenario = self.__outline_scenario_formatter
        
        # Deferring output.
        self.scenario_outline_header = self.__out.getvalue()
        self.__out = self.__real_out


    def background(self, bg):
        if bg.status == 'done':
            self.silent_steps = False
            return
        
        if bg.first_run:
            bg_name = self.format_name(bg.kw_i18n, bg.name)
            self.print_feature_header()
            self.set_source_indent(bg.steps, len(bg_name))
            self.__out.write(''.join(
                ('\n', ' ' * self.scenario_indent, bg_name, '\n')
            ))
            
            self.silent_steps = False
        else:
            self.silent_steps = True


    def step(self, step):
        if step.status is None:
            return
            
        self.counts[step.status] += 1

        if self.snippets and step.status == 'undefined' and step.name not in self.undefined:
            self.undefined[step.name] = (step.section, step.multi)

        if self.silent_steps:
            return
        
        # Get colors.
        regular = getattr(self.color_scheme, step.status, lambda x: x)
        highlight = getattr(self.color_scheme, '%s_param' % step.status, None)
        
        kw, name, multi, indent = step.kw_i18n, step.name, step.multi, ' ' * self.step_indent
           
        formatted = [
            indent,
            self.format_name(
                regular(kw), 
                regular(name)
                    if highlight is None or step.match is None else 
                highlight_groups(
                    step.match.matchobj, 
                    regular, 
                    highlight
                )
            ),
        ]
        
        # Print source of steps and scenarios.
        if self.source:
            source_indent = self.source_indent - len(kw) - len(name)
            if step.match:
                formatted.append(self.format_source(
                    step.match.source_file, step.match.source_line, source_indent
                ))
            else:
                formatted.append(self.format_source(
                    self.current_feature.filename, step.lineno, source_indent
                ))

        formatted.append('\n')
        
        # Print mulitiline args.
        if self.multiline and multi is not None:
            multiline_indent = ' ' * self.multiline_indent
            if type(multi) == types.StringType:
                # PyString
                formatted.extend((
                    '%s%s\n' % (multiline_indent, regular(s)) for s in ['"""'] + multi.split('\n') + ['"""']
                ))
            else:
                # Table
                fields, rows, w = multi.columns, multi.rows, multi.widths
                
                # Print table.
                colors = [regular] * len(fields)
                widths = [w[f] for f in fields]
                table = [multiline_indent, self.format_table_row(zip(fields, colors, widths)), '\n']
                for row in rows:
                    table.extend(
                        (multiline_indent,  self.format_table_row(zip([row[f] for f in fields], colors, widths)), '\n')
                    )                
                formatted.extend(table)
            
        self.__out.write(''.join(formatted))

        if step.exception and (self.strict or step.status != 'undefined'):
            self.print_exception(step.exception, step.tb, step.status)
