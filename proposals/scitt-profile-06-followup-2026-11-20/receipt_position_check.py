#!/usr/bin/env python3
"""Does an RFC9162_SHA256 inclusion path fix the tree size it is read with?

First-party check written from RFC 9162 Section 2.1 only, standard library
only, no network, no keys. An RFC 9942 Receipt of inclusion signs the Merkle
root (Section 5.2.1) and carries the tree size and leaf index outside the
signed protected header. If one inclusion path recomputes the same root under
two tree sizes, the Receipt's signature cannot tell those sizes apart.

This is not a Receipt implementation, a VCP verifier or a conformance test.
It checks the tree arithmetic behind the result reported on the SCITT list
(https://github.com/AugmentEV/rfc9942-receipt-position); it does not run that
repository's code.

Usage: python3 receipt_position_check.py [--max-leaves N]
"""

import argparse
import hashlib


def _h(data):
    return hashlib.sha256(data).digest()


def leaf_hash(entry):
    return _h(b"\x00" + entry)


def node_hash(left, right):
    return _h(b"\x01" + left + right)


def _split(n):
    """Largest power of two strictly less than n (RFC 9162 Section 2.1.1)."""
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def mth(entries):
    """Merkle Tree Hash, RFC 9162 Section 2.1.1."""
    if len(entries) == 1:
        return leaf_hash(entries[0])
    k = _split(len(entries))
    return node_hash(mth(entries[:k]), mth(entries[k:]))


def inclusion_path(m, entries):
    """Inclusion proof, RFC 9162 Section 2.1.3.1."""
    if len(entries) == 1:
        return []
    k = _split(len(entries))
    if m < k:
        return inclusion_path(m, entries[:k]) + [mth(entries[k:])]
    return inclusion_path(m - k, entries[k:]) + [mth(entries[:k])]


def root_from_path(leaf_index, tree_size, entry, path):
    """Verification steps of RFC 9162 Section 2.1.3.2; the root, or None."""
    if leaf_index >= tree_size:
        return None
    fn, sn, r = leaf_index, tree_size - 1, leaf_hash(entry)
    for p in path:
        if sn == 0:
            return None
        if fn % 2 == 1 or fn == sn:
            r = node_hash(p, r)
            while fn % 2 == 0 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            r = node_hash(r, p)
        fn >>= 1
        sn >>= 1
    return r if sn == 0 else None


def entries_of(size):
    return [i.to_bytes(2, "big") for i in range(size)]


def other_sizes(leaf_index, size, max_size):
    """Tree sizes other than `size`, up to max_size, under which the honest
    path for (leaf_index, size) recomputes the same root."""
    entries = entries_of(size)
    root = mth(entries)
    path = inclusion_path(leaf_index, entries)
    return [s for s in range(1, max_size + 1)
            if s != size and root_from_path(leaf_index, s, entries[leaf_index], path) == root]


def enumerate_pairs(max_leaves):
    """(pairs, pairs with another size): sizes 1..max_leaves, alternative
    sizes searched up to 4 * max_leaves - 1."""
    pairs = ambiguous = 0
    for size in range(1, max_leaves + 1):
        for i in range(size):
            pairs += 1
            if other_sizes(i, size, 4 * max_leaves - 1):
                ambiguous += 1
    return pairs, ambiguous


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--max-leaves", type=int, default=64)
    args = parser.parse_args()

    entries = entries_of(7)
    path = inclusion_path(5, entries)
    root = mth(entries)
    print("leaf 5 of 7, path read with tree size 8, same root:",
          root_from_path(5, 8, entries[5], path) == root)
    print("control, path read as leaf 4 of 7, same root:",
          root_from_path(4, 7, entries[5], path) == root)
    pairs, ambiguous = enumerate_pairs(args.max_leaves)
    print(f"tree sizes 1..{args.max_leaves}: {ambiguous} of {pairs} (size, index) pairs "
          "also recompute their root under another tree size")


if __name__ == "__main__":
    main()
