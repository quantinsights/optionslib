"""Testing suite for sorting algorithms."""

import unittest

from optionslib.algorithms.sort import quick_sort


class TestQuickSort(unittest.TestCase):
    """Unit tests for quick_sort."""

    def test_quicksort1(self):
        arr = [4, 6, 2, 5, 7, 9, 1, 3]
        quick_sort(arr)
        self.assertEqual(arr, [1, 2, 3, 4, 5, 6, 7, 9])
