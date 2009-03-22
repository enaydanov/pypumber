#!/usr/bin/env python

import types, itertools, sys
from peg import PEGParser
from feature_grammar import feature

class FeatureParser(PEGParser):
    _shadowed_non_terminals = ['line_to_eol', 'ts', 's', 'feature', 'step', 'tag_name']
    _skipped_non_terminals = ['space', 'eol', 'white', 'comment', 'open_py_string', 'close_py_string']
    _dict_non_terminals = ['step', 'scenario', 'feature', 'background']
    
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
        if type(r) == types.TupleType and r[0] == 'tags':
            return r
        
        if (r is not None) and (type(r) == types.TupleType) and (type(r[1]) == types.ListType) and (len(r[1]) > 1):
            for x in r[1]:
                if (type(x) != types.StringType) and (len(x) != 1):
                    break
            else:
                return (r[0], ''.join(r[1]))
        return r
  
    def step_keyword(self, subtree):
        from i18n_grammar import _language
        return _language(subtree), subtree
    
    def tags(self, subtree):
        return [t for _, t in subtree]
    
    def steps(self, subtree):
        """Handler for 'steps' non-terminal.
        
        Calculate source_indent for steps in out scenario.
        Each step is list of dicts: [{'step_keyword: (..., ...), 'name': ..., ...), ...]
        We need to calculate sum of lenght of two first.
        """
        lengths = [len(step['step_keyword'][1]) + len(step['name']) for step in subtree]
        max_length = max(lengths)
        assert len(subtree) == len(lengths)
        for step, indent in itertools.izip(subtree, (max_length - l + 2 for l in lengths)):
            step['source_indent'] = indent
        return subtree


if __name__ == '__main__':
    pass
