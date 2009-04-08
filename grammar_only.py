import sys, os, re
from pprint import pprint

def make_path(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.insert(0, make_path('lib'))

from peg import PEGParser, Node
from gherkin.feature_grammar import feature
from gherkin.languages import set_language

set_language('en')

class Parser(PEGParser):
    _shadowed_non_terminals = ['s', 'indent', 'multiline_arg', 'py_string', ]
    _skipped_non_terminals = ['space', 'comment', 'white', 'quotes', 'eol', 'open_py_string', 'close_py_string']
    #~ def py_string(self, subtree):
        #~ pass
    
    def s(self, subtree):
        return ''.join(subtree)
    
    def indent(self, subtree):
        return len(subtree)
    
    def py_string(self, subtree):
        return re.sub(r'^[ \t]{0,%d}' % subtree[0], '', subtree[1])
    

parser = Parser(feature)

#pprint(parser('examples\\scenario_outline_failing_background.feature'))
#path=['examples\\complex.feature', ]
pprint(parser('tmp\\a.feature'))
#path=['examples\\self_test\\features\\sample.feature', ]
