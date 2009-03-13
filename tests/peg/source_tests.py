#! /usr/bin/env python

import re, os, sys, unittest

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from peg.source import Source, SourceType
from StringIO import StringIO

class TestSource(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("The quick brown fox jumps over the lazy dog"))
    
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.text.cur, 0)
        self.assertEqual(self.text.text, "The quick brown fox jumps over the lazy dog")
    
    def test_001_substr(self):
        self.assertEqual(self.text.substr(3), "The")
        
        self.text.cur += 10
        self.assertEqual(self.text.substr(5), "brown")
        self.text.cur += 10
        self.assertEqual(self.text.substr(100), "jumps over the lazy dog")
        
    def test_002_substr_edge(self):
        self.text.cur = len(self.text.text)
        self.assertEqual(self.text.substr(100), "")
    
    def test_003_regexp(self):
        self.assertEqual(self.text.regexp(re.compile(r'\w+')), "The")
        self.text.cur += 10
        self.assertEqual(self.text.regexp(re.compile(r'\w+')), "brown")
        self.assertEqual(self.text.regexp(re.compile(r'\d+')), None)

		
class TestSourceType(unittest.TestCase):
    def test_000_constants(self):
        SourceType.GUESS
        SourceType.STRING
        SourceType.URL
        SourceType.FILE
        SourceType.STDIN

    def test_001_get_opener_for_string(self):
        opener = SourceType.opener(SourceType.STRING)
        source = opener("string")
        self.assert_(hasattr(source, 'read'))
        self.assertEqual(source.read(), "string")

    def test_002_get_opener_for_url(self):
        # TODO
        pass
    
    def test_003_get_opener_for_file(self):
        opener = SourceType.opener(SourceType.FILE)
        filename = os.path.join(os.path.dirname(__file__), 'sourcetype_file.txt')
        source = opener(filename)
        self.assert_(hasattr(source, 'read'))
        self.assertEqual(source.read(), "file")
        
    def test_004_get_opener_for_stdin(self):
        old_stdin = sys.stdin
        try:
            opener = SourceType.opener(SourceType.STDIN)
            sys.stdin = open(os.path.join(os.path.dirname(__file__), 'sourcetype_file.txt'))
            source = opener('-')
            self.assert_(hasattr(source, 'read'))
            self.assertEqual(source.read(), "file")
        finally:
            sys.stdin = old_stdin

    def test_005_guess_string(self):
        opener = SourceType.opener(SourceType.GUESS)
        source = opener("string")
        self.assert_(hasattr(source, 'read'))
        self.assertEqual(source.read(), "string")

    def test_006_guess_url(self):
        # TODO
        pass
    
    def test_007_guess_file(self):
        opener = SourceType.opener(SourceType.GUESS)
        filename = os.path.join(os.path.dirname(__file__), 'sourcetype_file.txt')
        source = opener(filename)
        self.assert_(hasattr(source, 'read'))
        self.assertEqual(source.read(), "file")
        
    def test_008_guess_stdin(self):
        old_stdin = sys.stdin
        try:
            opener = SourceType.opener(SourceType.GUESS)
            sys.stdin = open(os.path.join(os.path.dirname(__file__), 'sourcetype_file.txt'))
            source = opener('-')
            self.assert_(hasattr(source, 'read'))
            self.assertEqual(source.read(), "file")
        finally:
            sys.stdin = old_stdin

    def test_009_guess_filelike(self):
        opener = SourceType.opener(SourceType.GUESS)
        source = opener(open(os.path.join(os.path.dirname(__file__), 'sourcetype_file.txt')))
        self.assert_(hasattr(source, 'read'))
        self.assertEqual(source.read(), "file")

		
if __name__ == '__main__':
    unittest.main()
