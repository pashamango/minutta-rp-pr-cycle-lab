#!/usr/bin/env python3
"""Reference Ed25519 signer for Polymarket US API.
Prepared by Muse, verified by agy@wolfram.
"""

from __future__ import annotations

import base64
import os
import sys
import time
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import ed25519


def create_auth_headers(
    key_id: str,
    secret_key_b64: str,
    method: str,
    path: str,
    timestamp_ms: Optional[int] = None,
) -> dict[str, str]:
    """Pure reference function matching official polymarket_us/auth.py."""
    if timestamp_ms is None:
        timestamp_ms = int(time.time() * 1000)

    ts_str = str(timestamp_ms)
    message = f"{ts_str}{method.upper()}{path}".encode("utf-8")

    key_bytes = base64.b64decode(secret_key_b64)
    if len(key_bytes) == 64:
        key_bytes = key_bytes[:32]
    elif len(key_bytes) != 32:
        raise ValueError(f"Invalid secret key length: {len(key_bytes)}")

    priv = ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes)
    sig_bytes = priv.sign(message)
    sig_b64 = base64.b64encode(sig_bytes).decode("ascii")

    return {
        "X-PM-Access-Key": key_id,
        "X-PM-Timestamp": ts_str,
        "X-PM-Signature": sig_b64,
    }


def self_test() -> bool:
    """Run reference self-test: ephemeral keypair, sign, verify, zero network."""
    priv = ed25519.Ed25519PrivateKey.generate()
    seed_bytes = priv.private_bytes_raw()
    secret_b64 = base64.b64encode(seed_bytes).decode("ascii")
    key_id = "test-ref-key-id"

    method = "GET"
    path = "/v1/account/balances"
    headers = create_auth_headers(key_id, secret_b64, method, path)

    assert headers["X-PM-Access-Key"] == key_id
    assert headers["X-PM-Timestamp"].isdigit()
    assert len(base64.b64decode(headers["X-PM-Signature"])) == 64

    # Verify
    pub = priv.public_key()
    msg = f"{headers['X-PM-Timestamp']}{method}{path}".encode("utf-8")
    pub.verify(base64.b64decode(headers["X-PM-Signature"]), msg)
    print("Reference signer self-test: PASS (zero network)")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(0 if self_test() else 1)
    print("Usage: signer_reference.py --self-test")
