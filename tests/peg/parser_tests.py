#!/usr/bin/env python

import unittest, re, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from peg.parser import *
from peg.source import Source
from StringIO import StringIO


class TestOperator(unittest.TestCase):
    def test_000_empty_list(self):
        def create():
            And()
        self.assertRaises(SyntaxError, create)
    
    def test_001_one(self):
        self.assertEqual(And(1).pattern, 1)
        
    def test_002_multiple(self):
        self.assertEqual(And(1, 2).pattern, (1, 2))
    
    def test_003_tuple(self):
        self.assertEqual(And((1, 2)).pattern, (1, 2))
        
    def test_004_list(self):
        self.assertEqual(And([1, 2]).pattern, [1, 2])


class TestStringTerminal(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dog food"))
        
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser("dog")        
        self.assertEqual(parser._grammar, "dog")
        
    def test_001_string_terminal(self):
        parser = PEGParser("dog")        
        self.assertEqual(parser(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_string_terminal_fail(self):
        parser = PEGParser("fox")
        def tmp():
            parser(self.text)
        self.assertRaises(SyntaxError, tmp)
    
    def test_003_string_terminal_empty(self):
        parser = PEGParser("")
        old_cur = self.text.cur
        self.assertEqual(parser(self.text), "")
        self.assertEqual(old_cur, self.text.cur)
    
    def test_007_string_terminal_at_the_end(self):
        self.text.cur = 7
        def tmp():
            PEGParser("d  ")(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 7)

    #~ def test_008_string_terminal_after_the_end(self):
        #~ self.assertEqual(self.parser.string_terminal(self.text, "dog food"), "dog food")
        #~ self.assertEqual(self.text.cur, len(self.text.text))
        #~ def tmp():
            #~ self.parser.string_terminal(self.text, "  ")
        #~ self.assertRaises(SyntaxError, tmp)
    
    def test_009_string_terminal_empty_after_the_end(self):
        p_all = PEGParser("dog food")
        self.assertEqual(p_all(self.text), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        cur = self.text.cur
        p_nothing = PEGParser("")
        self.assertEqual(p_nothing(self.text), "")
        self.assertEqual(self.text.cur, cur)


class TestReTerminal(unittest.TestCase):
    def setUp(self):
        self.parser = PEGParser(re.compile(r'\w+'))
        self.text = Source(StringIO("dog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser._grammar.pattern, r'\w+')
        
    def test_003_re_terminal(self):
        self.assertEqual(self.parser(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_004_re_terminal_fail(self):
        def tmp():
            PEGParser(re.compile(r'\d+'))(self.text)
        self.assertRaises(SyntaxError, tmp)
    
    #~ def test_005_re_terminal_multiple(self):
        #~ self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\w+')), "dog")
        #~ self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\s+')), " ")
        #~ self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\w+')), "food")
    
    def test_006_re_terminal_empty(self):
        self.assertEqual(PEGParser(re.compile(r'\d*'))(self.text), "")
    
    def test_007_re_terminal_at_the_end(self):
        self.text.cur = 7
        def tmp():
            PEGParser(re.compile(r'\w+.+'))(self.text)
        self.assertRaises(SyntaxError, tmp)

    def test_008_re_terminal_after_the_end(self):
        self.assertEqual(PEGParser(re.compile(r'.*'))(self.text), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        def tmp():
            PEGParser(re.compile(r'.+'))(self.text)
        self.assertRaises(SyntaxError, tmp)
    
    def test_009_re_terminal_empty_after_the_end(self):
        self.assertEqual(PEGParser(re.compile(r'.*'))(self.text), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        cur = self.text.cur
        self.assertEqual(PEGParser(re.compile(r'.*'))(self.text), "")
        self.assertEqual(self.text.cur, cur)


class TestZeroOrOne(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dog food"))
    
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser(ZeroOrOne("dog"))
        self.assertEqual(parser._grammar.__class__.__name__, "ZeroOrOne")
        self.assertEqual(parser._grammar.pattern, "dog")
        
    def test_001_zero_or_one__one(self):
        self.assertEqual(PEGParser(ZeroOrOne("dog"))(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_zero_or_one__zero(self):
        parser = PEGParser(ZeroOrOne("fox"))
        self.assertEqual(parser(self.text), None)
        self.assertEqual(self.text.cur, 0)
    

        
class TestZeroOrMore(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dogdogdog food"))
    
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser(ZeroOrMore("dog"))
        self.assertEqual(parser._grammar.__class__.__name__, "ZeroOrMore")
        self.assertEqual(parser._grammar.pattern, "dog")
    
    def test_001_zero_or_more__one(self):
        self.assertEqual(PEGParser(ZeroOrMore("dogd"))(self.text), ["dogd"])
        self.assertEqual(self.text.cur, 4)
        
    def test_002_zero_or_more__more(self):
        self.assertEqual(PEGParser(ZeroOrMore("dog"))(self.text), ["dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 9)

    def test_003_zero_or_more__zero(self):
        self.assertEqual(PEGParser(ZeroOrMore("fox"))(self.text), None)
        self.assertEqual(self.text.cur, 0)


class TestOneOrMore(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dogdogdogdog food"))
    
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser(OneOrMore("dog"))
        self.assertEqual(parser._grammar.__class__.__name__, "OneOrMore")
        self.assertEqual(parser._grammar.pattern, "dog")
    
    def test_001_one_or_more__one(self):
        self.assertEqual(PEGParser(OneOrMore("dogd"))(self.text), ["dogd"])
        self.assertEqual(self.text.cur, 4)

    def test_002_one_or_more__two(self):
        self.assertEqual(PEGParser(OneOrMore("dogdog"))(self.text), ["dogdog", "dogdog"])
        self.assertEqual(self.text.cur, 12)
        
    def test_003_one_or_more__more(self):
        self.assertEqual(PEGParser(OneOrMore("dog"))(self.text), ["dog", "dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 12)

    def test_004_one_or_more__zero(self):
        def tmp():
            PEGParser(OneOrMore("fox"))(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)


class TestNot(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dog food"))
        
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser(Not("fox"))
        self.assertEqual(parser._grammar.__class__.__name__, "Not")
        self.assertEqual(parser._grammar.pattern, "fox")
        
    def test_001_not(self):
        self.assertEqual(PEGParser(Not("fox"))(self.text), None)
        self.assertEqual(self.text.cur, 0)
    
    def test_002_not__fail(self):
        def tmp():
            PEGParser(Not("dog"))(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

 
class TestAnd(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dog food"))
        
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser(And("dog"))
        self.assertEqual(parser._grammar.__class__.__name__, "And")
        self.assertEqual(parser._grammar.pattern, "dog")
        
    def test_001_and(self):
        self.assertEqual(PEGParser(And("dog"))(self.text), None)
        self.assertEqual(self.text.cur, 0)
    
    def test_002_and__fail(self):
        def tmp():
            PEGParser(And("fox"))(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)


class TestNonTerminal(unittest.TestCase):
    def setUp(self):
        def dog():
            return "dog"
        self.dog = dog
        self.parser = PEGParser(dog)
        self.text = Source(StringIO("dogdog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser._grammar, self.dog)

    def test_001_non_terminal(self):
        self.assertEqual(self.parser(self.text)(), ('dog', "dog"))
        self.assertEqual(self.text.cur, 3)

    def test_002_non_terminal__shadowed(self):
        def _dog():
            return "dog"
        class TmpParser(PEGParser):
            _shadowed_non_terminals = ['_dog']
        self.assertEqual(TmpParser(_dog)(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_003_non_terminal__skipped(self):
        def _dog():
            return "dog"
        class TmpParser(PEGParser):
            _skipped_non_terminals = ['_dog']
        self.assertEqual(TmpParser(_dog)(self.text), None)
        self.assertEqual(self.text.cur, 3)
        

    def test_004_non_terminal__nameerror(self):
        def dog():
            return dodog
        def tmp():
            PEGParser(dog)(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)


class TestAlternative(unittest.TestCase):
    def setUp(self):
        self.text = Source(StringIO("dogdog food"))
        
    def tearDown(self):
        del(self.text)
    
    def test_000_creation(self):
        parser = PEGParser(["dog", "foxy"])
        self.assertEqual(parser._grammar, ["dog", "foxy"])
        
    def test_001_alternative__first(self):
        self.assertEqual(PEGParser(["dog", "foxy"])(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_alternative__second(self):
        self.assertEqual(PEGParser(["foxy", "dog"])(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_003_alternative__shorter_first(self):
        self.assertEqual(PEGParser(["dog", "dogd"])(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_004_alternative__longer_first(self):
        self.assertEqual(PEGParser(["dogd", "dog"])(self.text), "dogd")
        self.assertEqual(self.text.cur, 4)
    
    def test_005_alternative__fail(self):
        def tmp():
            PEGParser(["foxy", "cat"])(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_006_alternative__empty(self):
        def tmp():
            PEGParser([])(self.text)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)


# TODO:
class TestSequence(unittest.TestCase): pass


#~ class TestCachingPEGParser(unittest.TestCase):
    #~ class Cache(object):
        #~ def __init__(self):
            #~ self.store = {}
            #~ self.getCount = {}
        
        #~ def __contains__(self, key):
            #~ return key in self.store
        
        #~ def __getitem__(self, key):
            #~ self.getCount[key] += 1
            #~ return self.store[key]
        
        #~ def __setitem__(self, key, value):
            #~ if key in self.store:
                #~ raise Exception
            #~ self.store[key] = value
            #~ self.getCount[key] = 0

    #~ def test_000_simple(self):
        #~ cache = self.Cache()
        #~ c = sys.getrefcount(cache)
        #~ self.assertEqual(CachingPEGParser((And("dog"), "dog"))("dogy dog", cache=cache), "dog")
        #~ self.assertEqual(c, sys.getrefcount(cache))
        #~ self.assertEqual(cache.store[(0, "dog")][0], "dog")
        #~ self.assertEqual(cache.getCount[(0, "dog")], 1)


if __name__ == '__main__':
    unittest.main()
