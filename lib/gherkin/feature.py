#!/usr/bin/env python

import os.path, types

from feature_grammar import feature
from mypeg import PEGParser


class FeatureParser(PEGParser):
    def __init__(self):
        PEGParser.__init__(self, feature)
    
    def non_terminal(self, text, pattern):
        r = PEGParser.non_terminal(self, text, pattern)
        if r is not None and type(r) == types.TupleType and type(r[1]) == types.ListType and len(r[1]) > 1:
            for x in r[1]:
                if type(x) != types.StringType and len(x) != 1:
                    break
            else:
                return (r[0], ''.join(r[1]))
        return r
    
    def step(self, name, subtree):
        d = dict(subtree)
        if d['step_keyword'] in ['Given', 'When', 'Then']:
            self.current_step_keyword = d['step_keyword']
        else:
            d['step_keyword'] = self.current_step_keyword
        
        return d
    
    def scenario(self, name, subtree):
        return name, dict(subtree)
    
    def feature_elements(self, name, subtree):
        return name, list([subtree])
    
    def feature(self, name, subtree):
        return dict(subtree)
        

if __name__ == '__main__':
    pass