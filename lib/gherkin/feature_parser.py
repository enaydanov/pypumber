#!/usr/bin/env python

import types, itertools, sys
from peg import PEGParser
from feature_grammar import feature

class FeatureParser(PEGParser):
    _shadowed_non_terminals = [
        'line_to_eol', 'ts', 's', 'feature', 'step', 'tag_name', 'multiline_arg', 
        'py_string', 'cell', 'cells', 'table_row', 'table',
    ]
    _skipped_non_terminals = [
        'space', 'eol', 'white', 'comment', 'quotes', 'open_py_string', 
        'close_py_string',
    ]
    _dict_non_terminals = ['step', 'scenario', 'feature', 'background', ]
    
    def __init__(self):
        super(FeatureParser, self).__init__(feature)

        # Make handlers for non-terminals which will be represented as dictionaries.
        def dict_non_terminal(subtree):
            return dict(subtree)

        for nt in self._dict_non_terminals:
            setattr(self, nt, dict_non_terminal)
    
    def _non_terminal(self, pattern):
        r = super(FeatureParser, self)._non_terminal(pattern)
        
        # Don't join tags in one string :)
        if type(r) == types.TupleType and len(r) and r[0] == 'tags':
            return r
        
        if (r is not None) and (type(r) == types.TupleType) and (type(r[1]) == types.ListType) and (len(r[1]) > 1):
            for x in r[1]:
                if (type(x) != types.StringType) and (len(x) != 1):
                    break
            else:
                return (r[0], ''.join(r[1]))
        return r

    def step_keyword(self, subtree):
        # Import here because language will be defined in run-time.
        from i18n_grammar import _language
        return _language(subtree), subtree, self._source.lineno()
    
    def scenario_keyword(self, subtree):
        return ''.join(subtree), self._source.lineno()
    
    def scenario_outline_keyword(self, subtree):
        return ''.join(subtree), self._source.lineno()
    
    def tags(self, subtree):
        return [t for _, t in subtree]
        
    def cell(self, subtree):
        if subtree is None:
            return ''
        return subtree
    
    def table_row(self, subtree):
        return tuple([s.strip() for s in subtree if s != '|'])
    
    def table(self, subtree):
        try:
            tbl = []
            names = subtree[0]
            tbl.append(tuple(names))
            for row in subtree[1:]:
                tbl.append(dict(zip(names, row)))
        except:
            raise SyntaxError()
        return tbl

if __name__ == '__main__':
    pass
