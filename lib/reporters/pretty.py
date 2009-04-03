#! /usr/bin/env python

import sys, os.path, types, traceback, string, collections

from cfg.set_defaults import set_defaults
from reporter import Reporter
from colors import ColoredOutput, highlight_groups
from snippet import snippet


class PrettyReporter(Reporter):
    def __init__(self):
        set_defaults(self, 'backtrace', 'color_scheme', 'source', 'multiline', 'snippets', 'strict')
        self.__out = ColoredOutput(sys.stdout)

        self.silent_steps = False
        self.current_feature = None
        self.talign = string.center

        # Indents.
        self.scenario_indent = 2
        self.step_indent = 4
        self.table_indent = 6
        self.traceback_indent = 6
        self.source_indent = 0  # will be recalculated for each scenario

        # Statistics.
        self.counts = collections.defaultdict(int)
        
        # Deferred output.
        self.feature_header = None

        # Scenario formatter by default.
        self.scenario = self.__default_scenario_formatter
        
        # Set of undefined steps.
        self.undefined = set()

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

    #
    # Format helpers.
    # 

    def set_source_indent(self, steps, minimal):
        lengths = [self.scenario_indent - self.step_indent + minimal,]
        if steps is not None:
            lengths.extend([len(step.kw_i18n) + len(step.name) for step in steps])
        self.source_indent = max(lengths) + 1


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
            rv.append(color(self.talign(value, width+2)))
        rv.append('')
        
        return '|'.join(rv)


    def print_feature_header(self):
        if self.feature_header is not None:
            self.__out.write(self.feature_header)
            self.feature_header = None


    def print_exception(self, exception, tb):
        if self.backtrace and tb:
            error_message = traceback.format_exception(type(exception), exception, tb)
        else:
            error_message = traceback.format_exception_only(type(exception), exception)
        error_message = ''.join(error_message).split('\n')
        indent = ' ' * self.traceback_indent
        formatted = []
        for line in error_message:
            formatted.extend((indent + line, '\n'))

        self.__out.write(self.color_scheme.failed(''.join(formatted)))


    def print_snippets(self):
        if self.undefined:
            formatted = ["\nYou can implement step definitions for missing steps with these snippets:\n", ]
            for kw, name in self.undefined:
                formatted.append('\n')
                formatted.append(snippet(kw, name))
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
        sc_len = len(kw) + len(name)
        self.set_source_indent(sc.steps, sc_len)
        
        # Print Scenario line.
        formatted.extend((indent, '%s %s' % (kw, name)))
        
        # Print source of scenario.
        if self.source:
            formatted.append(self.format_source(
                self.current_feature.filename,
                sc.lineno,
                self.source_indent - sc_len + self.step_indent - self.scenario_indent
            ))
        
        formatted.append('\n')
        
        self.__out.write(''.join(formatted))
                
        self.silent_steps = False


    def __outline_scenario_formatter(self, sc):
        if sc.status is None:
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
        
        if sc.exception and (self.strict or sc.status != 'undefined'):
            self.print_exception(sc.exception, sc.tb)

        # Statistics.
        self.counts['scenarios'] += 1


    def scenario_outline(self, sc):
        if sc.status == 'done':
            self.scenario = self.__default_scenario_formatter
        else:
            self.counts['scenarios'] -= 1
            self.print_feature_header()


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


    def background(self, bg):
        if bg.first_run:
            self.print_feature_header()
            self.set_source_indent(bg.steps, len(bg.kw_i18n))
            self.__out.write(''.join(
                ('\n', ' ' * self.scenario_indent, bg.kw_i18n, '\n')
            ))
            
            self.silent_steps = False
        else:
            self.silent_steps = True


    def step(self, step):
        if step.status is None:
            return
            
        self.counts[step.status] += 1

        if self.silent_steps:
            return
        
        # Get colors.
        regular = getattr(self.color_scheme, step.status, lambda x: x)
        highlight = getattr(self.color_scheme, '%s_param' % step.status, None)
        
        kw, name, multi, indent = step.kw_i18n, step.name, step.multi, ' ' * self.step_indent
           
        formatted = [indent, regular(kw), ' ']
        formatted.append(
            regular(name)
                if highlight is None or step.match is None else 
            highlight_groups(
                step.match.matchobj, 
                regular, 
                highlight
            )
        )
        
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
            if type(multi) == types.StringType:
                # PyString
                formatted.append(regular(
                    '%s"""\n%s\n%s"""\n' % (indent, multi, indent)
                ))
            else:
                # Table
                fields, rows, w = multi.columns, multi.rows, multi.widths
                
                # Table row prefix.
                table_indent = ' ' * self.table_indent
                
                # Print table.
                colors = [regular] * len(fields)
                widths = [w[f] for f in fields]
                table = [table_indent, self.format_table_row(zip(fields, colors, widths)), '\n']
                for row in rows:
                    table.extend(
                        (table_indent,  self.format_table_row(zip([row[f] for f in fields], colors, widths)), '\n')
                    )                
                formatted.extend(table)
        
        self.__out.write(''.join(formatted))

        if step.exception and (self.strict or step.status != 'undefined'):
            self.print_exception(step.exception, step.tb)
        
        if self.snippets and step.status == 'undefined':
            self.undefined.add((step.section, step.name))
