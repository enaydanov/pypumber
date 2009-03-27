#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


from subst_params import subst_params

class Table(object):
    """Table object."""
    def __init__(self, raw):
        self.raw = raw
        self.rebuild(raw)
        
    def rebuild(self, raw):
        """Rebuild table from raw."""
        self.columns = tuple(raw[0])
        self.rows = []
        for row in raw[1:]:
            self.rows.append(dict(zip(self.columns, row)))

    def subst(self, pattern, values):
        """Substitue values into header and cells."""
        raw = []
        used = set()
        
        for row in self.raw:
            raw.append(
                reduce(
                    lambda x, y: x[0].append(y[0]) or x[1].update(y[1]) or x, 
                    (subst_params(f, pattern, values) for f in row), 
                    ([], used)
                )[0]
            )
        self.rebuild(raw)
        
        return used

    @property
    def widths(self):
        """Returns dictionary with calculated widths of columns."""
        rv = {}
        for col in self.columns:
            rv[col] = max(len(col), max(len(row[col]) for row in self.rows))
        
        return rv

    def __repr__(self):
        return str([self.columns, self.rows])
