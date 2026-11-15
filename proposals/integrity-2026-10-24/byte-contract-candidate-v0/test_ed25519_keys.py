"""Configured-key admission regressions, separate from frozen byte vectors."""
import base64
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import contract as c

HERE = Path(__file__).resolve().parent
P = 2**255 - 19
SMALL_ORDER_KEYS = (
    "0100000000000000000000000000000000000000000000000000000000000000",
    "ecffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff7f",
    "0000000000000000000000000000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000000000000000000000000080",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc05",
    "26e8958fc2b227b045c3f489f2ef98f0d5dfac05d3c63339b13802886d53fc85",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac037a",
    "c7176a703d4dd84fba3c0b760d10670f2a2053fa2c39ccc64ec7fd7792ac03fa",
)
FORGED = base64.b64encode(bytes.fromhex(SMALL_ORDER_KEYS[0]) + bytes(32)).decode()


class KeyAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads((HERE / "data/vectors.json").read_text())

    def test_eight_points_are_distinct_and_killed_by_the_cofactor(self):
        # Test-only RFC 8032 decoding and doubling checks the hard-coded table.
        d = -121665 * pow(121666, -1, P) % P
        root_minus_one = pow(2, (P - 1) // 4, P)
        seen = set()
        for key in SMALL_ORDER_KEYS:
            integer = int.from_bytes(bytes.fromhex(key), "little")
            y, sign = integer & (2**255 - 1), integer >> 255
            xx = (y * y - 1) * pow(d * y * y + 1, -1, P) % P
            x = pow(xx, (P + 3) // 8, P)
            if x * x % P != xx:
                x = x * root_minus_one % P
            self.assertEqual(x * x % P, xx)
            if x & 1 != sign:
                x = -x % P
            self.assertEqual(x & 1, sign)
            self.assertNotIn((x, y), seen)
            seen.add((x, y))
            for _ in range(3):
                product = d * x * x * y * y % P
                x, y = (2 * x * y * pow(1 + product, -1, P) % P,
                        (y * y + x * x) * pow(1 - product, -1, P) % P)
            self.assertEqual((x, y), (0, 1))
        self.assertEqual(len(seen), 8)

    def test_small_order_keys_are_rejected_before_backend_verification(self):
        with patch.object(c.Ed25519PublicKey, "from_public_bytes") as backend:
            for key in SMALL_ORDER_KEYS:
                with self.subTest(key=key):
                    self.assertFalse(c.raw_verify(key, FORGED, b"arbitrary message"))
            backend.assert_not_called()

    def test_noncanonical_points_cannot_bypass_admission(self):
        values = [y | (sign << 255) for y in range(P, 2**255) for sign in (0, 1)]
        values += [y | (1 << 255) for y in (1, P - 1)]
        with patch.object(c.Ed25519PublicKey, "from_public_bytes") as backend:
            for value in values:
                with self.subTest(value=value):
                    self.assertFalse(c.raw_verify(value.to_bytes(32, "little").hex(), FORGED, b"message"))
            backend.assert_not_called()

    def test_identity_signature_cannot_authenticate_either_statement_role(self):
        for kind, row in (("event_signature", self.vectors["event_signatures"][0]),
                          ("anchor_signature", self.vectors["anchor"])):
            with self.subTest(kind=kind):
                statement = row["statement"]
                identity = (kind, statement["ProducerID"], statement["StreamID"], statement["KeyID"])
                self.assertEqual(c.signature_check(statement, FORGED, kind,
                                                   {identity: SMALL_ORDER_KEYS[0]}), "fail")

    def test_malformed_configured_key_is_a_failed_check_not_a_crash(self):
        valid = self.vectors["public_test_keys"]["event"]["public_key_hex"]
        for value in (None, 1, True, [], {}, "", "00" * 31, "00" * 33,
                      valid.upper(), valid + "\n", " ".join(valid[i:i+2] for i in range(0, 64, 2))):
            with self.subTest(value=value):
                self.assertFalse(c.raw_verify(value, FORGED, b"message"))

    def test_existing_keys_still_require_the_signature_equation(self):
        for kind, role, row in (("event_signature", "event", self.vectors["event_signatures"][0]),
                                ("anchor_signature", "anchor", self.vectors["anchor"])):
            key = self.vectors["public_test_keys"][role]["public_key_hex"]
            message = c.signature_preimage(row["statement"], kind)
            self.assertTrue(c.raw_verify(key, row["signature"], message))
            self.assertFalse(c.raw_verify(key, row["signature"], message + b"changed"))
            self.assertFalse(c.raw_verify(key, FORGED, message))

    def test_missing_selected_key_remains_unknown(self):
        row = self.vectors["event_signatures"][0]
        self.assertEqual(c.signature_check(row["statement"], row["signature"],
                                           "event_signature", {}), "unknown")


if __name__ == "__main__":
    unittest.main()
