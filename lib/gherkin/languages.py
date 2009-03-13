#! /usr/bin/env python

class keywords(object):
    def __init__(self, lang):
        self.lang = lang
        self.keywords = {'given': 'given', 'when': 'when', 'then': 'then'}
    
    def __getattr__(self, attr):
        if attr in self.keywrods:
            return self.keywords[attr]
        raise AttributeError()

    def __str__(self):
        str = []
        for k, v in self.keywords.items():
            str.append("%s: %s" % (k, v))
        return "\n".join(str)


class Languages(object):
    def __init__(self):
        self.languages = ['en', 'ru']
    
    def __iter__(self):
        return iter(self.languages)
    
    def __getitem__(self, key):
        if key not in self.languages:
            raise KeyError()
        return keywords(key)

    def __contains__(self, key):
        return key in self.languages
