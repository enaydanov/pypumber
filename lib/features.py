#! /usr/bin/env python

from gherkin import FeatureParser, set_language
from peg import SourceType
from find_files import find_files
from cfg.set_defaults import set_defaults
from collections import defaultdict
from split_feature_path import split_feature_path


class Features(object):
    def __init__(self):
        set_defaults(self, 'path', 'excludes')
        self.__current_language = None
        self.__parser = FeatureParser()
    
    # 'lang' property
    def get_lang(self):
        return self.__current_language
    def set_lang(self, language):
        if language != self.__current_language:
            set_language(language)
            self.__current_language = language
    lang = property(get_lang, set_lang)

    def __iter__(self):
        paths = []
        for path in self.path:
            feature, lines = split_feature_path(path)
            if lines:
                yield (feature, self.__parser(feature, SourceType.FILE), lines)
                continue
            paths.append(path)
        
        for feature in find_files(paths, '*.feature', self.excludes):
            yield (feature, self.__parser(feature, SourceType.FILE), None)
