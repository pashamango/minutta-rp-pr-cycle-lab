#!/usr/bin/env python3
"""Deterministic counterexamples for POW-0001's pure 2-adic predicate."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time


def inverse3_newton(k: int) -> int:
    """Return 3^-1 modulo 2^k, doubling valid precision per iteration."""
    if k < 1:
        raise ValueError("k must be at least 1")
    y = 1
    bits = 1
    while bits < k:
        bits = min(2 * bits, k)
        y = (y * (2 - 3 * y)) % (1 << bits)
    return y


def solve(a: int, k: int, inverse3: int) -> int:
    return (-inverse3 - a) % (1 << k)


def valid(a: int, x: int, k: int) -> bool:
    return (3 * (a + x) + 1) % (1 << k) == 0


def derive(label: bytes, index: int, k: int) -> int:
    raw = hashlib.sha256(label + index.to_bytes(16, "big")).digest()
    value = int.from_bytes(raw, "big")
    while value.bit_length() < k:
        raw = hashlib.sha256(raw).digest()
        value = (value << 256) | int.from_bytes(raw, "big")
    return value % (1 << k)


def timed_candidates(label: bytes, count: int, k: int, inverse3: int) -> dict:
    checksum = 0
    start = time.perf_counter_ns()
    for i in range(count):
        a = derive(label, i, k)
        x = solve(a, k, inverse3)
        if not valid(a, x, k):
            raise AssertionError((label, i, a, x, k))
        checksum ^= x
    elapsed = time.perf_counter_ns() - start
    return {
        "candidates": count,
        "elapsed_ns": elapsed,
        "candidates_per_second": count * 1_000_000_000 / elapsed,
        "ns_per_candidate": elapsed / count,
        "checksum": hex(checksum),
    }


def result_record(count: int, elapsed: int, checksum: int) -> dict:
    return {
        "candidates": count,
        "elapsed_ns": elapsed,
        "candidates_per_second": count * 1_000_000_000 / elapsed,
        "ns_per_candidate": elapsed / count,
        "checksum": hex(checksum),
    }


def parallel_forks(forks: int, levels: int, k: int, inverse3: int) -> dict:
    common_parent = hashlib.sha256(b"common-parent").digest()
    tips = [common_parent] * forks
    checksum = 0
    start = time.perf_counter_ns()
    for level in range(levels):
        for fork in range(forks):
            material = tips[fork] + fork.to_bytes(8, "big") + level.to_bytes(8, "big")
            a = int.from_bytes(hashlib.sha256(material).digest(), "big") % (1 << k)
            x = solve(a, k, inverse3)
            if not valid(a, x, k):
                raise AssertionError(("fork", fork, level, a, x, k))
            tips[fork] = hashlib.sha256(material + x.to_bytes((k + 7) // 8, "big")).digest()
            checksum ^= x
    return result_record(forks * levels, time.perf_counter_ns() - start, checksum)


def offline_rewrite(blocks: int, k: int, inverse3: int) -> dict:
    tip = hashlib.sha256(b"historical-checkpoint").digest()
    checksum = 0
    start = time.perf_counter_ns()
    for height in range(blocks):
        material = tip + height.to_bytes(16, "big")
        a = int.from_bytes(hashlib.sha256(material).digest(), "big") % (1 << k)
        x = solve(a, k, inverse3)
        if not valid(a, x, k):
            raise AssertionError(("rewrite", height, a, x, k))
        tip = hashlib.sha256(material + x.to_bytes((k + 7) // 8, "big")).digest()
        checksum ^= x
    return result_record(blocks, time.perf_counter_ns() - start, checksum)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identities", type=int, default=100_000)
    parser.add_argument("--forks", type=int, default=1_000)
    parser.add_argument("--levels", type=int, default=100)
    parser.add_argument("--rewrite-blocks", type=int, default=100_000)
    args = parser.parse_args()
    if min(args.identities, args.forks, args.levels, args.rewrite_blocks) < 1:
        parser.error("all counts must be positive")

    result = {
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "parameters": vars(args),
        "width_costs": {},
        "attacks": {},
    }
    for k in (32, 64, 128, 256, 512):
        start = time.perf_counter_ns()
        inverse3 = inverse3_newton(k)
        inverse_elapsed = time.perf_counter_ns() - start
        if (3 * inverse3) % (1 << k) != 1:
            raise AssertionError(("inverse", k))
        sample_count = 50_000
        measured = timed_candidates(b"width-cost", sample_count, k, inverse3)
        measured["inverse_precompute_ns"] = inverse_elapsed
        result["width_costs"][str(k)] = measured

    k = 256
    inverse3 = inverse3_newton(k)
    result["attacks"]["sybil_block_factory"] = timed_candidates(
        b"identity", args.identities, k, inverse3
    )
    result["attacks"]["parallel_fork_factory"] = parallel_forks(
        args.forks, args.levels, k, inverse3
    )
    result["attacks"]["offline_history_rewrite"] = offline_rewrite(
        args.rewrite_blocks, k, inverse3
    )
    result["checks"] = {
        "all_candidates_valid": True,
        "inverse_is_precomputed_once_per_width": True,
        "external_scarce_resource_consumed": False,
        "mainnet_interaction": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
