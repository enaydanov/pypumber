#!/usr/bin/env python

import unittest, re
import mypeg
from StringIO import StringIO


class TestText(unittest.TestCase):
    def setUp(self):
        self.text = mypeg.Text(StringIO("The quick brown fox jumps over the lazy dog"))
    
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


class TestOperator(unittest.TestCase):
    def test_000_empty_list(self):
        def create():
            mypeg.And()
        self.assertRaises(SyntaxError, create)
    
    def test_001_one(self):
        self.assertEqual(mypeg.And(1).pattern, 1)
        
    def test_002_multiple(self):
        self.assertEqual(mypeg.And(1, 2).pattern, (1, 2))
    
    def test_003_tuple(self):
        self.assertEqual(mypeg.And((1, 2)).pattern, (1, 2))
        
    def test_004_list(self):
        self.assertEqual(mypeg.And([1, 2]).pattern, [1, 2])


class TestStringTerminal(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser("dog")
        self.text = mypeg.Text(StringIO("dog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar, "dog")
        
    def test_001_string_terminal(self):
        self.assertEqual(self.parser.string_terminal(self.text, "dog"), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_string_terminal_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, "dog"), "dog")
        self.assertEqual(self.text.cur, 3)
    
    def test_003_string_terminal_as_default(self):
        self.assertEqual(self.parser.parse(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_004_string_terminal_fail(self):
        def tmp():
            self.parser.string_terminal(self.text, "fox")
        self.assertRaises(SyntaxError, tmp)
    
    def test_005_string_terminal_multiple(self):
        self.assertEqual(self.parser.string_terminal(self.text, "dog"), "dog")
        self.assertEqual(self.parser.string_terminal(self.text, " "), " ")
        self.assertEqual(self.parser.string_terminal(self.text, "food"), "food")
    
    def test_006_string_terminal_empty(self):
        self.assertEqual(self.parser.string_terminal(self.text, ""), "")
    
    def test_007_string_terminal_at_the_end(self):
        self.parser.string_terminal(self.text, "dog foo")
        def tmp():
            self.parser.string_terminal(self.text, "d  ")
        self.assertRaises(SyntaxError, tmp)

    def test_008_string_terminal_after_the_end(self):
        self.assertEqual(self.parser.string_terminal(self.text, "dog food"), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        def tmp():
            self.parser.string_terminal(self.text, "  ")
        self.assertRaises(SyntaxError, tmp)
    
    def test_009_string_terminal_empty_after_the_end(self):
        self.assertEqual(self.parser.string_terminal(self.text, "dog food"), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        cur = self.text.cur
        self.assertEqual(self.parser.string_terminal(self.text, ""), "")
        self.assertEqual(self.text.cur, cur)


class TestReTerminal(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(re.compile(r'\w+'))
        self.text = mypeg.Text(StringIO("dog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar.pattern, r'\w+')
        
    def test_001_re_terminal(self):
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\w+')), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_re_terminal_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, re.compile(r'\w+')), "dog")
        self.assertEqual(self.text.cur, 3)
    
    def test_003_re_terminal_as_default(self):
        self.assertEqual(self.parser.parse(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_004_re_terminal_fail(self):
        def tmp():
            self.parser.re_terminal(self.text, re.compile(r'\d+'))
        self.assertRaises(SyntaxError, tmp)
    
    def test_005_re_terminal_multiple(self):
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\w+')), "dog")
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\s+')), " ")
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\w+')), "food")
    
    def test_006_re_terminal_empty(self):
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'\d*')), "")
    
    def test_007_re_terminal_at_the_end(self):
        self.parser.string_terminal(self.text, "dog foo")
        def tmp():
            self.parser.re_terminal(self.text, re.compile(r'\w+.+'))
        self.assertRaises(SyntaxError, tmp)

    def test_008_re_terminal_after_the_end(self):
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'.*')), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        def tmp():
            self.parser.re_terminal(self.text, re.compile(r'.+'))
        self.assertRaises(SyntaxError, tmp)
    
    def test_009_re_terminal_empty_after_the_end(self):
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'.*')), "dog food")
        self.assertEqual(self.text.cur, len(self.text.text))
        cur = self.text.cur
        self.assertEqual(self.parser.re_terminal(self.text, re.compile(r'.*')), "")
        self.assertEqual(self.text.cur, cur)


class TestZeroOrOne(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(mypeg.ZeroOrOne("dog"))
        self.text = mypeg.Text(StringIO("dog food"))
    
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar.__class__.__name__, "ZeroOrOne")
        self.assertEqual(self.parser.grammar.pattern, "dog")
        
    def test_001_zero_or_one__one(self):
        self.assertEqual(self.parser.zero_or_one(self.text, mypeg.ZeroOrOne("dog")), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_zero_or_one__zero(self):
        self.assertEqual(self.parser.zero_or_one(self.text, mypeg.ZeroOrOne("fox")), None)
        self.assertEqual(self.text.cur, 0)
        
    def test_003_zero_or_one_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, mypeg.ZeroOrOne("dog")), "dog")
        self.assertEqual(self.text.cur, 3)
    
    def test_004_zero_or_one_as_default(self):
        self.assertEqual(self.parser.parse(self.text), "dog")
        self.assertEqual(self.text.cur, 3)

        
class TestZeroOrMore(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(mypeg.ZeroOrMore("dog"))
        self.text = mypeg.Text(StringIO("dogdogdog food"))
    
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar.__class__.__name__, "ZeroOrMore")
        self.assertEqual(self.parser.grammar.pattern, "dog")
    
    def test_001_zero_or_more__one(self):
        self.assertEqual(self.parser.zero_or_more(self.text, mypeg.ZeroOrMore("dogd")), "dogd")
        self.assertEqual(self.text.cur, 4)
        
    def test_002_zero_or_more__more(self):
        self.assertEqual(self.parser.zero_or_more(self.text, mypeg.ZeroOrMore("dog")), ["dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 9)

    def test_003_zero_or_more__zero(self):
        self.assertEqual(self.parser.zero_or_more(self.text, mypeg.ZeroOrMore("fox")), None)
        self.assertEqual(self.text.cur, 0)

    def test_004_zero_or_more_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, mypeg.ZeroOrMore("dog")), ["dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 9)
    
    def test_005_zero_or_more_as_default(self):
        self.assertEqual(self.parser.parse(self.text), ["dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 9)


class TestOneOrMore(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(mypeg.OneOrMore("dog"))
        self.text = mypeg.Text(StringIO("dogdogdogdog food"))
    
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar.__class__.__name__, "OneOrMore")
        self.assertEqual(self.parser.grammar.pattern, "dog")
    
    def test_001_one_or_more__one(self):
        self.assertEqual(self.parser.one_or_more(self.text, mypeg.OneOrMore("dogd")), "dogd")
        self.assertEqual(self.text.cur, 4)

    def test_002_one_or_more__two(self):
        self.assertEqual(self.parser.one_or_more(self.text, mypeg.OneOrMore("dogdog")), ["dogdog", "dogdog"])
        self.assertEqual(self.text.cur, 12)
        
    def test_003_one_or_more__more(self):
        self.assertEqual(self.parser.one_or_more(self.text, mypeg.OneOrMore("dog")), ["dog", "dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 12)

    def test_004_one_or_more__zero(self):
        def tmp():
            self.parser.one_or_more(self.text, mypeg.OneOrMore("fox"))
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_005_one_or_more_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, mypeg.OneOrMore("dog")), ["dog", "dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 12)
    
    def test_006_one_or_more_as_default(self):
        self.assertEqual(self.parser.parse(self.text), ["dog", "dog", "dog", "dog"])
        self.assertEqual(self.text.cur, 12)


class TestNot(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(mypeg.Not("fox"))
        self.text = mypeg.Text(StringIO("dog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar.__class__.__name__, "Not")
        self.assertEqual(self.parser.grammar.pattern, "fox")
        
    def test_001_not(self):
        self.assertEqual(self.parser.not_predicate(self.text, mypeg.Not("fox")), None)
        self.assertEqual(self.text.cur, 0)
    
    def test_002_not__fail(self):
        def tmp():
            self.parser.not_predicate(self.text, mypeg.Not("dog"))
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_003_not_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, mypeg.Not("fox")), None)
        self.assertEqual(self.text.cur, 0)
    
    def test_004_not_as_default(self):
        self.assertEqual(self.parser.parse(self.text), None)
        self.assertEqual(self.text.cur, 0)
    

class TestAnd(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(mypeg.And("dog"))
        self.text = mypeg.Text(StringIO("dog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar.__class__.__name__, "And")
        self.assertEqual(self.parser.grammar.pattern, "dog")
        
    def test_001_and(self):
        self.assertEqual(self.parser.and_predicate(self.text, mypeg.And("dog")), None)
        self.assertEqual(self.text.cur, 0)
    
    def test_002_and__fail(self):
        def tmp():
            self.parser.and_predicate(self.text, mypeg.And("fox"))
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_003_and_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, mypeg.Not("fox")), None)
        self.assertEqual(self.text.cur, 0)
    
    def test_004_and_as_default(self):
        self.assertEqual(self.parser.parse(self.text), None)
        self.assertEqual(self.text.cur, 0)


class TestNonTerminal(unittest.TestCase):
    def setUp(self):
        def dog():
            return "dog"
        self.dog = dog
        self.parser = mypeg.PEGParser(dog)
        self.text = mypeg.Text(StringIO("dogdog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar, self.dog)

    def test_001_non_terminal(self):
        self.assertEqual(self.parser.non_terminal(self.text, self.dog), ('dog', "dog"))
        self.assertEqual(self.text.cur, 3)

    def test_002_non_terminal__shadowed(self):
        def _dog():
            return "dog"
        self.assertEqual(self.parser.non_terminal(self.text, _dog), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_003_non_terminal__skipped(self):
        def __dog():
            return "dog"
        self.assertEqual(self.parser.non_terminal(self.text, __dog), None)
        self.assertEqual(self.text.cur, 3)
        

    def test_004_non_terminal__nameerror(self):
        def dog():
            return dodog
        def tmp():
            self.parser.non_terminal(self.text, dog)
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_005_non_terminal_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, self.dog), ('dog', "dog"))
        self.assertEqual(self.text.cur, 3)
    
    def test_006_non_terminal_as_default(self):
        self.assertEqual(self.parser.parse(self.text), ('dog', "dog"))
        self.assertEqual(self.text.cur, 3)
   

class TestAlternative(unittest.TestCase):
    def setUp(self):
        self.parser = mypeg.PEGParser(["dog", "foxy"])
        self.text = mypeg.Text(StringIO("dogdog food"))
        
    def tearDown(self):
        del(self.parser)
        del(self.text)
    
    def test_000_creation(self):
        self.assertEqual(self.parser.grammar, ["dog", "foxy"])
        
    def test_001_alternative__first(self):
        self.assertEqual(self.parser.alternative(self.text, ["dog", "foxy"]), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_002_alternative__second(self):
        self.assertEqual(self.parser.alternative(self.text, ["foxy", "dog"]), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_003_alternative__shorter_first(self):
        self.assertEqual(self.parser.alternative(self.text, ["dog", "dogd"]), "dog")
        self.assertEqual(self.text.cur, 3)

    def test_004_alternative__longer_first(self):
        self.assertEqual(self.parser.alternative(self.text, ["dogd", "dog"]), "dogd")
        self.assertEqual(self.text.cur, 4)
    
    def test_005_alternative__fail(self):
        def tmp():
            self.parser.alternative(self.text, ["foxy", "cat"])
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_006_alternative__empty(self):
        def tmp():
            self.parser.alternative(self.text, [])
        self.assertRaises(SyntaxError, tmp)
        self.assertEqual(self.text.cur, 0)

    def test_007_alternative_via_parse(self):
        self.assertEqual(self.parser.parse(self.text, ["dog", "foxy"]), "dog")
        self.assertEqual(self.text.cur, 3)
    
    def test_008_alternative_as_default(self):
        self.assertEqual(self.parser.parse(self.text), "dog")
        self.assertEqual(self.text.cur, 3)


# TODO:
class TestSequence(unittest.TestCase): pass


if __name__ == '__main__':
    unittest.main()
    