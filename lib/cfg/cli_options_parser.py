#! /usr/bin/env python

import sys, copy, textwrap, optparse
from gherkin.languages import Languages
from version import version

class PypumberHelpFormatter(optparse.IndentedHelpFormatter):
    """Pypumber Help Formatter.
    
    This is IndentedHelpFormatter with small changes:
        1. max_help_position = 40
        2. It doesn't show arg name for short options.
        3. Format for long options is "--opt OPT"
        4. It splits help text by blank line and show as separate paragraphs.
    """
    class S(object):
        def __mod__(self, arg):
            return "%s" % arg[0]

    def __init__(self):
        optparse.IndentedHelpFormatter.__init__(self, max_help_position=40)
        self._short_opt_fmt = self.S()
        self._long_opt_fmt = "%s %s"

    def format_option(self, option):
        result = []
        opts = self.option_strings[option]
        opt_width = self.help_position - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_position
        else:                       # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_text = self.expand_default(option)
            help_lines = []
            for t in help_text.split("\n\n"):
                help_lines.extend(textwrap.wrap(t, self.help_width))
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_position, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)

def check_language(option, opt, value):
    if value == 'help' or value in Languages():
        return value
    raise optparse.OptionValueError('unsupported language: %s' % value)

class PypumberOption (optparse.Option):
    """Pypumber command line option type.
    
    It contains standard optparse.Option types and actions + type `language' and actions 
    `store_or_help' and `comma_separated'.
    
    Type `language' checks for supported languages.
    
    Action `store_or_help' shows help if first arg is 'help' and help for first arg if second arg is 
    'help'. E.g. --language help, --language en help. If first arg is not 'help' it stores it.
    
    Action `comma_separated' splits first arg by comma and stores it as list of values.
    """
    TYPES = optparse.Option.TYPES + ("language",)
    TYPE_CHECKER = copy.copy(optparse.Option.TYPE_CHECKER)
    TYPE_CHECKER["language"] = check_language
    ACTIONS = optparse.Option.ACTIONS + ("store_or_help", "comma_separated")
    STORE_ACTIONS = optparse.Option.STORE_ACTIONS + ("store_or_help", "comma_separated")
    TYPED_ACTIONS = optparse.Option.TYPED_ACTIONS + ("store_or_help", "comma_separated")
    ALWAYS_TYPED_ACTIONS = optparse.Option.ALWAYS_TYPED_ACTIONS + ("store_or_help", "comma_separated",)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "store_or_help":
            try:
                if value == 'help':
                    parser.help_callbacks[dest]()
                    sys.exit()
                elif len(parser.rargs) and parser.rargs[0] == 'help':
                    del(parser.rargs[0])
                    parser.help_callbacks[dest](value)
                    sys.exit()
            except KeyError:
                raise optparse.OptionValueError('no help for option: %s' % opt)
            setattr(values, dest, value)
        elif action == "comma_separated":
            v = tuple(value.split(","))
            setattr(values, dest, v)
        else:
            optparse.Option.take_action(self, action, dest, opt, value, values, parser)


class PypumberOptionParser(optparse.OptionParser):
    def __init__(self, usage, version):
        optparse.OptionParser.__init__(self, 
            usage=usage, 
            version=version, 
            option_class=PypumberOption, 
            formatter=PypumberHelpFormatter()
        )
        self.help_callbacks = {}
    
    def set_help_callbacks(self, **kw):
        for (k, v) in kw.items():
            self.help_callbacks[k] = v


# Callbacks
def quiet_option_callback(option, opt_str, value, parser):
    parser.values.snippets = False
    parser.values.source = False

def dry_run_option_callback(option, opt_str, value, parser):
    setattr(parser.values, 'dry_run', True)
    quiet_option_callback(option, opt_str, value, parser)

def autoformat_option_callback(option, opt_str, value, parser):
    dry_run_option_callback(option, opt_str, value, parser)
    parser.values.color = False
    parser.values.formatter = 'pretty'
    setattr(parser.values, option.dest, value)

# TODO:
def lang_help_callback(lang=None):
    languages = Languages()
    if lang is None:
        for l in languages:
            print l
    else:
        print languages[lang]


usage = """Usage: pypumber [options] [ [FILE|DIR|URL][:LINE[:LINE]*] ]+
    
Examples:
pypumber examples/i18n/en/features
pypumber --language it examples/i18n/it/features/somma.feature:6:98:113
pypumber -n -i http://rubyurl.com/eeCl
"""

parser = PypumberOptionParser(usage, version)

parser.set_help_callbacks(
    lang=lang_help_callback
)

parser.add_option("-r", "--require", metavar="LIBRARY|DIR", action="append",
    help="Require files before executing the features. If this option is not specified, " 
    "all *.py files that are siblings or below the features will be loaded automatically. " 
    "Automatic loading is disabled when this option is specified, and all loading becomes "
    "explicit. Files under directories named \"support\" are always loaded first."
    "\n\n"
    "This option can be specified multiple times.")

parser.add_option("-l", "--language", action="store_or_help", metavar="LANG", type="language", dest="lang",
    help="Specify language for features (Default: %default)"
    "\n\n"
    "Run with \"--language help\" to see all languages"
    "\n\n"
    "Run with \"--language LANG help\" to list keywords for LANG")

# INCOMPATIBLE:
parser.add_option("-f",  "--format", metavar="FORMAT", dest="active_format",
    help="How to format features (Default: %default) "
    "Available formats: #{FORMATS.join(\", \")} "
    "You can also provide your own formatter classes as long "
    "as they have been previously required using --require or "
    "if they are in the folder structure such that pypumber "
    "will require them automatically."
    "\n\n"
    "This option can be specified multiple times.")

# INCOMPATIBLE:
parser.add_option("-o", "--out", metavar="FILE", dest="output_filename",
    help="Write output to a file instead of STDOUT. This option "
    "applies to the previously specified --format, or the "
    "default format if no format is specified.")

parser.add_option("-t", "--tags", action="comma_separated",
    help="Only execute the features or scenarios with the specified tags. "
    "TAGS must be comma-separated without spaces. Prefix tags with ~ to "
    "exclude features or scenarios having that tag. Tags can be specified "
    "with or without the @ prefix.")

parser.add_option("-s", "--scenario", metavar="SCENARIO", action="append", dest="scenario_names",
    help="Only execute the scenario with the given name. If this option "
    "is given more than once, run all the specified scenarios.")

parser.add_option("-e", "--exclude", metavar="PATTERN", action="append", dest="excludes",
    help="Don't run feature files matching PATTERN.")

parser.add_option("-p", "--profile",
    help="Pull commandline arguments from pypumber.yml.")

parser.add_option("-c", "--color", action="store_true")
parser.add_option("--no-color", action="store_false", dest="color", 
    help="Whether or not to use ANSI color in the output. Pypumber decides "
    "based on your platform and the output destination if not specified.")

parser.add_option("-d", "--dry-run", action="callback", callback=dry_run_option_callback,
    help="Invokes formatters without executing the steps. Implies --quiet.")

parser.add_option("-a", "--autoformat", metavar="DIRECTORY", type="string", action="callback", callback=autoformat_option_callback,
    help="Reformats (pretty prints) feature files and write them to DIRECTORY. "
    "Be careful if you choose to overwrite the originals."
    "\n\n"
    "Implies --dry-run --formatter pretty.")

parser.add_option("-m", "--no-multiline", action="store_false", dest="multiline",
    help="Don't print multiline strings and tables under steps.")

parser.add_option("-n", "--no-source", action="store_false", dest="source",
    help="Don't print the file and line of the step definition with the steps.")

parser.add_option("-i", "--no-snippets", action="store_false", dest="snippets",
    help="Don't print snippets for pending steps.")

parser.add_option("-q", "--quiet", action="callback", callback=quiet_option_callback,
    help="Alias for --no-snippets --no-source.")

parser.add_option("-b", "--backtrace", action="store_true",
    help="Show full backtrace for all errors.")

parser.add_option("--strict", action="store_true",
    help="Fail if there are any undefined steps.")

parser.add_option("-v", "--verbose", action="store_true",
    help="Show the files and features loaded.")

parser.add_option("-g", "--guess", action="store_true", 
    help="Guess best match for Ambiguous steps.")
