#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

import re, string
from colors.highlight_groups import *


class TestCompactSpans(unittest.TestCase):
    def test_000_empty(self):
        spans = []
        self.assertEqual(compact_spans(spans), [])
    
    def test_001_one_equal(self):
        spans = [(1,1)]
        self.assertEqual(compact_spans(spans), [1, 1])
        
    def test_002_one_wrong(self):
        spans = [(2,1)]
        self.assertRaises(ValueError, compact_spans, spans)
    
    def test_003_two(self):
        spans = [(1,2), (3,4)]
        self.assertEqual(compact_spans(spans), [1, 2, 3, 4])

    def test_004_two_second_in_first(self):
        spans = [(1,4), (2,3)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_005_two_first_in_second(self):
        spans = [(2,3), (1,4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_006_two_second_in_first_same_start(self):
        spans = [(1,4), (1,3)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_007_two_first_in_second_same_start(self):
        spans = [(1,3), (1,4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_008_two_second_in_first_same_end(self):
        spans = [(1,4), (2,4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_009_two_first_in_second_same_end(self):
        spans = [(2,4), (1,4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_010_two_second_after_first(self):
        spans = [(1,2), (2,3)]
        self.assertEqual(compact_spans(spans), [1, 3])

    def test_011_two_first_after_second(self):
        spans = [(2,3), (1,2)]
        self.assertEqual(compact_spans(spans), [1, 3])

    def test_012_two_equal(self):
        spans = [(1,4), (1, 4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_013_three(self):
        spans = [(1,2), (3, 4), (5, 6)]
        self.assertEqual(compact_spans(spans), [1, 2, 3, 4, 5, 6])

    def test_014_three_not_in_order(self):
        spans = [(5, 6), (3, 4), (1, 2)]
        self.assertEqual(compact_spans(spans), [1, 2, 3, 4, 5, 6])

    def test_015_three_merge_first_two(self):
        spans = [(1, 2), (2, 4), (5, 6)]
        self.assertEqual(compact_spans(spans), [1, 4, 5, 6])

    def test_016_three_merge_first_and_last(self):
        spans = [(1, 2), (5, 6), (2, 4)]
        self.assertEqual(compact_spans(spans), [1, 4, 5, 6])

    def test_017_three_merge_last_two(self):
        spans = [(1, 2), (3, 4), (4, 6)]
        self.assertEqual(compact_spans(spans), [1, 2, 3, 6])

    def test_018_three_merge_last_two(self):
        spans = [(1, 2), (4, 6), (3, 4)]
        self.assertEqual(compact_spans(spans), [1, 2, 3, 6])

    def test_019_three_merge_all_1(self):
        spans = [(1, 2), (2, 3), (3, 4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_020_three_merge_all_2(self):
        spans = [(1, 2), (3, 4), (2, 3)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_021_three_merge_all_3(self):
        spans = [(3, 4), (1, 2), (2, 3)]
        self.assertEqual(compact_spans(spans), [1, 4])
    
    def test_022_three_last_eats_first(self):
        spans = [(1, 2), (3, 4), (1, 3)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_023_three_last_eats_second(self):
        spans = [(1, 2), (3, 4), (2, 4)]
        self.assertEqual(compact_spans(spans), [1, 4])

    def test_024_more_all_in_first(self):
        spans = [(1, 10), (2, 3), (4, 5), (6, 7), (8, 9)]
        self.assertEqual(compact_spans(spans), [1, 10])

    def test_025_more_all_in_last(self):
        spans = [(2, 3), (4, 5), (6, 7), (8, 9), (1, 10)]
        self.assertEqual(compact_spans(spans), [1, 10])


class TestHighlightGroups(unittest.TestCase):
    def test_000_empty(self):
        m = re.search(r'(\d+)', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), None)
    
    def test_001_no_groups(self):
        m = re.search(r'.+', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "some str")

    def test_002_whole_str(self):
        m = re.search(r'(.+)', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "SOME STR")

    def test_003_one_at_begin(self):
        m = re.search(r'(some)', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "SOME str")

    def test_004_one_at_end(self):
        m = re.search(r'(str)', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "some STR")

    def test_005_one_in_the_middle(self):
        m = re.search(r'(st)', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "some STr")

    def test_006_plus(self):
        m = re.search(r'(.)+', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "some stR")
    
    def test_007_many(self):
        m = re.search(r'(som)e (st)r', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "SOMe STr")

    def test_008_overlap(self):
        m = re.search(r'((som)e (st))r', "some str")
        self.assertEqual(highlight_groups(m, lambda x: x, string.upper), "SOME STr")
    

if __name__ == '__main__':
    unittest.main()
