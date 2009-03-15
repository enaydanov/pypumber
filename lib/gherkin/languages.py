#! /usr/bin/env python

import os, sys

from singleton import Singleton
from attribute_mapper import AttributeMapper

try:
    import yaml
except ImportError:
    sys.stderr.write("Error: unable to import PyYAML module. Please, download it from http://pyyaml.org\n")
    sys.exit()

languages_file = os.path.join(os.path.dirname(__file__), 'languages.yml')

class Languages(Singleton):
    def __init__(self):
        try:
            f = None
            f = open(languages_file)
            self.__yaml = yaml.load(f)
            for lang in self.__yaml:
                for k in self.__yaml[lang]:
                    if k not in ['name', 'native', 'encoding']:
                        self.__yaml[lang][k] = [alt.strip() for alt in self.__yaml[lang][k].split('|')]
        except IOError:
            sys.stderr.write("Error: unable to load languages from `%s'.\n" % languages_file)
            sys.exit()
        finally:
            if f:
                f.close()
        self.languages = self.__yaml.keys()
        self.languages.sort()
        self.kw_cmp = lambda a, b: a in b 

    def __iter__(self):
        return iter(self.languages)
    
    def __getitem__(self, key):
        if key not in self.languages:
            raise KeyError()
        return AttributeMapper(self.__yaml[key], self.kw_cmp)

    def __contains__(self, key):
        return key in self.languages

def set_language(lang):
    languages = Languages()
    if lang in languages:
        import i18n_grammar
        i18n_grammar._language = languages[lang]
    else:
        raise ValueError("unknown language: %s" % lang)
