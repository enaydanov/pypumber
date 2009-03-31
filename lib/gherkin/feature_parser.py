#!/usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


from peg import PEGParser, Node
from feature_grammar import feature
from table import Table
from scenario_outline import ScenarioOutline


class FeatureParser(PEGParser):
    _shadowed_non_terminals = [
        'line_to_eol', 'ts', 's', 'feature', 'step', 'tag_name', 'multiline_arg', 
        'cell', 'cells', 'table_row', 'scenario', 'scenario_outline', 'tag', 
        'examples', 'table', 'py_string',
    ]
    _skipped_non_terminals = [
        'space', 'eol', 'white', 'comment', 'quotes', 'open_py_string', 
        'close_py_string', 'eof',
    ]
    _string_non_terminals = [
        'header', 's', 'line_to_eol', 'background_keyword', 'examples_keyword', 
        'tag', 'py_string',
    ]
    
    def __init__(self):
        super(FeatureParser, self).__init__(feature)

        def string_non_terminal(subtree):
            """Handler for string non-terminals.
            
            Joins a list of strings or returns None if arg is None.
            """
            if subtree is not None: return ''.join(subtree)
        
        for nt in self._string_non_terminals:
            setattr(self, nt, string_non_terminal)

    # Strip names.
    def name(self, subtree):
        if subtree is not None: return subtree.strip()

    #
    # Step.
    #
    def step_keyword(self, subtree):
        """Handler for step keyword.
        
        Returns tuple: (kw, kw_i18n, lineno).
        """
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
        return Node(
            kw = subtree[0][1][0],
            kw_i18n = subtree[0][1][1],
            name = subtree[1][1] or '',
            multi = subtree[2][1],
            lineno = subtree[0][1][2],
        )
    
    #
    # Background.
    #
    def background(self, subtree):
        """Fill the background structure.
        
        Background will have following properties:
            1. kw
            2. kw_i18n
            3. steps
        """
        return Node(
            kw = 'background',
            kw_i18n = subtree[0][1],
            steps = subtree[1][1],
        )
    
    #
    # Scenario.
    #
    def scenario_keyword(self, subtree):
        """Handler for scenario keyword.
        
        Returns tuple: (kw_i18n, lineno).
        """
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
        return Node(
            kw = 'scenario',
            kw_i18n = subtree[1][1][0],
            name = subtree[2][1] or '',
            steps = subtree[3][1],
            tags = subtree[0][1],
            lineno = subtree[1][1][1],
        )
        
        return rv

    #
    # Sceario Outline.
    #
    def examples(self, subtree):
        """Fill the Examples structure.
        
        Examples will have following properties:
            1. kw
            2. kw_i18n
            3. name
            4. table
        """
        return Node(
            kw = 'examples',
            kw_i18n = subtree[0][1],
            name = subtree[1][1] or '',
            table = subtree[2],
        )

    def scenario_outline_keyword(self, subtree):
        """Handler for scenario outline keyword.
        
        Returns tuple: (kw_i18n, lineno).
        """
        return ''.join(subtree), self._source.lineno()
        
    def scenario_outline(self, subtree):
        """Fill the scenario outline structure.
        
        Each scenario outline will have following properties:
            1. kw 
            2. kw_i18n
            3. name
            4. steps
            5. examples
            6. tags
            7. lineno
        """
        rv = ScenarioOutline(
            kw = 'scenario_outline',
            kw_i18n = subtree[1][1][0],
            name = subtree[2][1] or '',
            steps = subtree[3][1],
            examples = subtree[4][1],
            tags = subtree[0][1],
            lineno = subtree[1][1][1],
        )

        # Backup templates.
        for step in rv.steps:
            step.name_template = step.name
            step.multi_template = step.multi

        return rv

    #
    # Feature.
    #
    def feature(self, subtree):
        return Node(**dict(subtree))

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
            return Table(subtree)
        except:
            raise SyntaxError("unable to build a Table from the subtree: %s" % subtree)

if __name__ == '__main__':
    pass
