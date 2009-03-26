#!/usr/bin/env python

import types, itertools, sys
from peg import PEGParser
from feature_grammar import feature

class FeatureParser(PEGParser):
    _shadowed_non_terminals = [
        'line_to_eol', 'ts', 's', 'feature', 'step', 'tag_name', 'multiline_arg', 
        'cell', 'cells', 'table_row', 'scenario', 'scenario_outline', 'tag', 
        'examples', 'table', 'py_string',
    ]
    _skipped_non_terminals = [
        'space', 'eol', 'white', 'comment', 'quotes', 'open_py_string', 
        'close_py_string',
    ]
    _string_non_terminals = [
        'header', 's', 'line_to_eol', 'background_keyword', 'examples_keyword', 
        'tag', 'py_string',
    ]
    
    def __init__(self):
        super(FeatureParser, self).__init__(feature)

        def string_non_terminal(subtree):
            if subtree is not None:
                return ''.join(subtree)
            return subtree
        
        for nt in self._string_non_terminals:
            setattr(self, nt, string_non_terminal)

    #
    # Step.
    #
    def step_keyword(self, subtree):
        # Import here because language will be defined in run-time.
        from i18n_grammar import _language
        return _language(subtree), subtree, self._source.lineno()
    
    def step(self, subtree):
        """Fill the step structure.
        
        Each step will have following properties:
            1. kw 
            2. kw_i18n
            3. name
            4. multi
            5. lineno
        """
        rv = {}
        rv['kw'] = subtree[0][1][0]
        rv['kw_i18n'] = subtree[0][1][1]
        rv['name'] = subtree[1][1]
        rv['multi'] = subtree[2][1]
        rv['lineno'] = subtree[0][1][2]
        
        return rv
    
    #
    # Background.
    #
    def background(self, subtree):
        """Fill the background structure.
        
        Background will have following properties:
            1. kw_i18n
            2. steps
        """
        rv = {}
        rv['kw_i18n'] = subtree[0][1]
        rv['steps'] = subtree[1][1]
        
        return rv
    
    #
    # Scenario.
    #
    def scenario_keyword(self, subtree):
        return ''.join(subtree), self._source.lineno()
    
    def scenario(self, subtree):
        """Fill the scenario structure.
        
        Each scenario will have following properties:
            1. kw 
            2. kw_i18n
            3. name
            4. steps
            5. tags
            6. lineno
        """
        rv = {}
        rv['kw'] = 'scenario'
        rv['kw_i18n'] = subtree[1][1][0]
        rv['name'] = subtree[2][1]
        rv['steps'] = subtree[3][1]
        rv['tags'] = subtree[0][1]
        rv['lineno'] = subtree[1][1][1]
        
        return rv

    #
    # Sceario Outline.
    #
    def examples(self, subtree):
        """Fill the scenario structure.
        
        Each scenario will have following properties:
            1. kw_i18n
            2. name
            3. table
        """
        rv = {}
        rv['kw_i18n'] = subtree[0][1]
        rv['name'] = subtree[1][1]
        rv['table'] = subtree[2:]
        
        return rv

    def scenario_outline_keyword(self, subtree):
        return ''.join(subtree), self._source.lineno()
        
    def scenario_outline(self, subtree):
        """Fill the scenario outline structure.
        
        Each scenario outline will have following properties:
            1. kw 
            2. kw_i18n
            3. name
            4. steps
            5. tags
            6. lineno
        """
        rv = {}
        rv['kw'] = 'scenario_outline'
        rv['kw_i18n'] = subtree[1][1][0]
        rv['name'] = subtree[2][1]
        rv['steps'] = subtree[3][1]
        rv['examples'] = subtree[4][1]
        rv['tags'] = subtree[0][1]
        rv['lineno'] = subtree[1][1][1]
        
        return rv

    #
    # Feature.
    #
    def feature(self, subtree):
        return dict(subtree)

    #
    # Table.
    #
    def cell(self, subtree):
        if subtree is None:
            return ''
        return ''.join(subtree)
    
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
