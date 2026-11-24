"""Tree-arithmetic regression for SCITT-VCP Open Issue 6 (position and size).

Checks the first-party RFC 9162 arithmetic in the proposal directory. It does
not test a Receipt implementation and adopts no VCP rule.
"""

import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROPOSAL = REPO / "proposals" / "scitt-profile-06-followup-2026-11-20"
SPEC = importlib.util.spec_from_file_location("receipt_position_check", PROPOSAL / "receipt_position_check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ReceiptPositionArithmetic(unittest.TestCase):
    def test_honest_paths_verify(self):
        for size in range(1, 33):
            entries = CHECK.entries_of(size)
            root = CHECK.mth(entries)
            for i in range(size):
                path = CHECK.inclusion_path(i, entries)
                self.assertEqual(CHECK.root_from_path(i, size, entries[i], path), root)

    def test_reported_case_seven_read_as_eight(self):
        self.assertIn(8, CHECK.other_sizes(5, 7, 64))

    def test_index_is_bound_for_fixed_size(self):
        entries = CHECK.entries_of(7)
        root = CHECK.mth(entries)
        path = CHECK.inclusion_path(5, entries)
        for i in range(7):
            if i != 5:
                self.assertNotEqual(CHECK.root_from_path(i, 7, entries[5], path), root)

    def test_not_every_pair_is_ambiguous(self):
        # The last leaf of a power-of-two tree has no other size: under a
        # larger size the path runs out before the root is reached.
        self.assertEqual(CHECK.other_sizes(7, 8, 64), [])

    def test_enumeration_matches_reported_count(self):
        self.assertEqual(CHECK.enumerate_pairs(64), (2080, 1984))


if __name__ == "__main__":
    unittest.main()
