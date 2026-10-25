"""Unit and integration tests for Polymarket US Ed25519 Request Signer.

STRICT ZERO-NETWORK GUARANTEE:
All tests execute purely in-memory using offline fixtures, RFC 8032 test vectors,
and official SDK cross-checks. Socket connections are blocked.
Runs seamlessly with either `python test_signer.py`, `python -m unittest`, or `pytest`.
"""

from __future__ import annotations

import base64
import os
import socket
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric import ed25519

from signer import (
    MAX_CLOCK_SKEW_SECONDS,
    RFC8032_V1_PUB_HEX,
    RFC8032_V1_SEED_HEX,
    RFC8032_V1_SIG_HEX,
    RFC8032_V2_MSG_HEX,
    RFC8032_V2_PUB_HEX,
    RFC8032_V2_SEED_HEX,
    RFC8032_V2_SIG_HEX,
    SDK_TEST_KEY_ID,
    SDK_TEST_SECRET_KEY,
    ClockSkewError,
    ConfigurationError,
    PolymarketSigner,
    parse_ed25519_seed,
    run_self_test,
)


class BaseZeroNetworkTestCase(unittest.TestCase):
    """Base test case ensuring no test makes socket/network connections."""

    def setUp(self):
        def no_connect(*args, **kwargs):
            raise RuntimeError("Network connection attempt detected in zero-network test suite!")

        self._patch_connect = patch.object(socket.socket, "connect", side_effect=no_connect)
        self._patch_sendto = patch.object(socket.socket, "sendto", side_effect=no_connect)
        self._patch_connect.start()
        self._patch_sendto.start()

    def tearDown(self):
        self._patch_sendto.stop()
        self._patch_connect.stop()


class TestSeedParsing(BaseZeroNetworkTestCase):
    """Tests for parse_ed25519_seed."""

    def test_valid_32_byte_seed(self):
        seed_32 = os.urandom(32)
        b64 = base64.b64encode(seed_32).decode()
        self.assertEqual(parse_ed25519_seed(b64), seed_32)

    def test_valid_64_byte_expanded_key(self):
        seed_32 = os.urandom(32)
        pub_32 = os.urandom(32)
        b64 = base64.b64encode(seed_32 + pub_32).decode()
        self.assertEqual(parse_ed25519_seed(b64), seed_32)

    def test_invalid_base64_raises(self):
        with self.assertRaises(ConfigurationError) as ctx:
            parse_ed25519_seed("invalid!base64!!")
        self.assertIn("not valid base64", str(ctx.exception))

    def test_invalid_length_raises(self):
        b64_16 = base64.b64encode(b"0" * 16).decode()
        with self.assertRaises(ConfigurationError):
            parse_ed25519_seed(b64_16)

        b64_48 = base64.b64encode(b"0" * 48).decode()
        with self.assertRaises(ConfigurationError):
            parse_ed25519_seed(b64_48)


class TestPolymarketSignerCore(BaseZeroNetworkTestCase):
    """Core signing and verification tests."""

    def test_ephemeral_roundtrip(self):
        signer = PolymarketSigner.ephemeral("test-uuid")
        self.assertEqual(signer.key_id, "test-uuid")
        self.assertEqual(len(signer.public_key_bytes), 32)

        headers = signer.sign_request("GET", "/v1/account/balances", timestamp_ms=1700000000000)
        self.assertEqual(headers["X-PM-Access-Key"], "test-uuid")
        self.assertEqual(headers["X-PM-Timestamp"], "1700000000000")

        raw_sig = base64.b64decode(headers["X-PM-Signature"])
        self.assertEqual(len(raw_sig), 64)

        pub = ed25519.Ed25519PublicKey.from_public_bytes(signer.public_key_bytes)
        self.assertTrue(
            PolymarketSigner.verify_signature(
                pub, "GET", "/v1/account/balances", "1700000000000", headers["X-PM-Signature"]
            )
        )

    def test_tamper_detection(self):
        signer = PolymarketSigner.ephemeral("test-uuid")
        headers = signer.sign_request("GET", "/v1/portfolio/positions", timestamp_ms=1700000000000)
        pub = ed25519.Ed25519PublicKey.from_public_bytes(signer.public_key_bytes)

        # Tampered method
        self.assertFalse(
            PolymarketSigner.verify_signature(
                pub, "POST", "/v1/portfolio/positions", "1700000000000", headers["X-PM-Signature"]
            )
        )

        # Tampered path
        self.assertFalse(
            PolymarketSigner.verify_signature(
                pub, "GET", "/v1/portfolio/other", "1700000000000", headers["X-PM-Signature"]
            )
        )

        # Tampered timestamp
        self.assertFalse(
            PolymarketSigner.verify_signature(
                pub, "GET", "/v1/portfolio/positions", "1700000000001", headers["X-PM-Signature"]
            )
        )

        # Tampered signature
        corrupted_sig = base64.b64encode(b"X" * 64).decode()
        self.assertFalse(
            PolymarketSigner.verify_signature(
                pub, "GET", "/v1/portfolio/positions", "1700000000000", corrupted_sig
            )
        )


class TestOfficialStandardsAndVectors(BaseZeroNetworkTestCase):
    """Verification against RFC 8032 and Official Polymarket US SDK vectors."""

    def test_rfc8032_vector_1(self):
        seed = bytes.fromhex(RFC8032_V1_SEED_HEX)
        signer = PolymarketSigner.from_seed_bytes("rfc1", seed)
        self.assertEqual(signer.public_key_bytes.hex(), RFC8032_V1_PUB_HEX)

        raw_sig = signer._private_key.sign(b"")
        self.assertEqual(raw_sig.hex(), RFC8032_V1_SIG_HEX)

    def test_rfc8032_vector_2(self):
        seed = bytes.fromhex(RFC8032_V2_SEED_HEX)
        signer = PolymarketSigner.from_seed_bytes("rfc2", seed)
        self.assertEqual(signer.public_key_bytes.hex(), RFC8032_V2_PUB_HEX)

        msg = bytes.fromhex(RFC8032_V2_MSG_HEX)
        raw_sig = signer._private_key.sign(msg)
        self.assertEqual(raw_sig.hex(), RFC8032_V2_SIG_HEX)

    def test_official_sdk_crosscheck(self):
        """Cross-check against official SDK polymarket_us/auth.py."""
        signer = PolymarketSigner.from_base64_secret(SDK_TEST_KEY_ID, SDK_TEST_SECRET_KEY)
        headers = signer.sign_request("POST", "/v1/orders", timestamp_ms=1700000000000)

        self.assertEqual(headers["X-PM-Access-Key"], SDK_TEST_KEY_ID)
        self.assertEqual(headers["X-PM-Timestamp"], "1700000000000")

        seed = base64.b64decode(SDK_TEST_SECRET_KEY)
        priv = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
        expected_sig = base64.b64encode(
            priv.sign("1700000000000POST/v1/orders".encode("utf-8"))
        ).decode("ascii")

        self.assertEqual(headers["X-PM-Signature"], expected_sig)

    def test_64_byte_key_matches_32_byte_key(self):
        seed_32 = base64.b64decode(SDK_TEST_SECRET_KEY)
        key_64_b64 = base64.b64encode(seed_32 + seed_32).decode("ascii")

        signer_32 = PolymarketSigner.from_base64_secret(SDK_TEST_KEY_ID, SDK_TEST_SECRET_KEY)
        signer_64 = PolymarketSigner.from_base64_secret(SDK_TEST_KEY_ID, key_64_b64)

        h32 = signer_32.sign_request("GET", "/v1/orders", timestamp_ms=1700000000000)
        h64 = signer_64.sign_request("GET", "/v1/orders", timestamp_ms=1700000000000)

        self.assertEqual(h32["X-PM-Signature"], h64["X-PM-Signature"])


class TestSecurityAndKeyScrubbing(BaseZeroNetworkTestCase):
    """Assurance that keys never leak into logs or string representations."""

    def test_repr_and_str_scrubbed(self):
        signer = PolymarketSigner.from_base64_secret("secret-id-99", SDK_TEST_SECRET_KEY)
        rep = repr(signer)
        s = str(signer)

        self.assertNotIn(SDK_TEST_SECRET_KEY, rep)
        self.assertNotIn(SDK_TEST_SECRET_KEY, s)
        self.assertIn("secret-id-99", rep)
        self.assertIn("Ed25519", rep)

    def test_env_loader_success(self):
        with patch.dict(
            os.environ,
            {
                "POLYMARKET_KEY_ID": "env-key-id",
                "POLYMARKET_SECRET_KEY": SDK_TEST_SECRET_KEY,
            },
        ):
            signer = PolymarketSigner.from_env()
            self.assertEqual(signer.key_id, "env-key-id")

    def test_env_loader_missing_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                PolymarketSigner.from_env()


class TestClockSkewProtection(BaseZeroNetworkTestCase):
    """Clock-skew detection and loud failure tests."""

    def test_clock_skew_pass_under_30s(self):
        with patch("signer.query_ntp_offset", return_value=5.4):
            offset = PolymarketSigner.verify_clock_skew(max_skew_seconds=30.0)
            self.assertEqual(offset, 5.4)

    def test_clock_skew_fail_over_30s(self):
        with patch("signer.query_ntp_offset", return_value=31.2):
            with self.assertRaises(ClockSkewError) as ctx:
                PolymarketSigner.verify_clock_skew(max_skew_seconds=30.0)
            self.assertIn("+31.20s exceeds", str(ctx.exception))

    def test_clock_skew_fail_negative_over_30s(self):
        with patch("signer.query_ntp_offset", return_value=-32.5):
            with self.assertRaises(ClockSkewError) as ctx:
                PolymarketSigner.verify_clock_skew(max_skew_seconds=30.0)
            self.assertIn("-32.50s exceeds", str(ctx.exception))

    def test_sign_with_clock_check_raises_when_skewed(self):
        signer = PolymarketSigner.ephemeral()
        with patch("signer.query_ntp_offset", return_value=45.0):
            with self.assertRaises(ClockSkewError):
                signer.sign_request("GET", "/v1/orders", check_clock=True)


class TestSelfTestRunner(BaseZeroNetworkTestCase):
    """Verifies that the standalone self-test function executes cleanly."""

    def test_run_self_test(self):
        self.assertTrue(run_self_test())


if __name__ == "__main__":
    unittest.main()
