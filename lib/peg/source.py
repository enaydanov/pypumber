#! /usr/bin/env python

import sys, urlparse, urllib, StringIO

def openAnything(source):
    if hasattr(source, 'read'):
        return source

    # stdin
    if source == '-':
        return sys.stdin
    
    # url
    if urlparse.urlparse(source)[0] == 'http':
        return urllib.urlopen(source)

    # Try file
    try:
        return open(source)
    except (IOError, OSError):
        pass

    # fallback: string
    return StringIO.StringIO(str(source))

	
class SourceType(object):
    GUESS, STRING, URL, FILE, STDIN = range(5)

    __map = [
        openAnything, # GUESS
        lambda x: StringIO.StringIO(x), # STRING
        urllib.urlopen, # URL
        open, # FILE
        lambda x: sys.stdin, # STDIN
    ]
    
    @staticmethod
    def opener(source_type):
        return SourceType.__map[source_type]


class Source(object):
    def __init__(self, source, source_type=SourceType.GUESS):
        if type(self) == type(source):
            self.text = source.text
            self.__cur = source
        else:
            self.text = SourceType.opener(source_type)(source).read()
            self.__cur = 0
   
    # 'cur' property.
    def get_cur(self):
        if type(self.__cur) == type(self):
            return self.__cur.cur
        else:
            return self.__cur
    def set_cur(self, value):
        if type(self.__cur) == type(self):
            self.__cur.cur = value
        else:
            self.__cur = value
    cur = property(get_cur, set_cur)
    
    def lineno(self, pos=None):
        if pos is None:
            pos = self.cur
        return self.text.count('\n', 0, pos) + 1

    def substr(self, length):
        """ Returns substring from current position with length `length' """
        if self.cur + length > len(self.text):
            return self.text[self.cur:]
        else:
            return self.text[self.cur:self.cur+length]
    
    def regexp(self, pattern):
        """ Returns matched string for pattern `pattern' from current position or None if matches not found """
        match = pattern.match(self.text, self.cur)
        if match is not None:
            return match.group()
