# COLLATZ-TAIL-0002 finite verification report

Issue: #23

## Result

```text
required cases: 1000
required transitions: 1000
required mismatches: 0
first counterexample or PASS: PASS
64-bit stretch cases: 1000
64-bit stretch mismatches: 0
```

This is finite computational verification only. It is not evidence for the
Collatz conjecture.

## Method and independence

`direct_successor` and `coordinate_successor` are separate functions. The
coordinate function finds `k` by increasing it from one while
`n == L_k (mod 2^k)`, strips with `q = (n - L_k) / 2^k`, and constructs its
successor only as `3*q + c_k`. It does not call the direct function or `v2`, and
does not inspect `3*n + 1`. A deterministic AST test checks these source-level
properties and the exact successor expression.

For `r(k) = ceil(k/2)` and `L_k = (4^r(k) - 1)/3`, the landmark identity

```text
3*L_k + 1 = 2^(2*r(k))
```

was checked for every `k` from 1 through 128. The test suite also checks, after
both evaluators return, that every successor is odd and that
`3*n + 1 == 2^k * m`.

The explanatory algebraic identity is:

```text
3*n + 1
= 3*(L_k + 2^k*q) + 1
= 2^k * (3*q + (3*L_k+1)/2^k)
= 2^k * (3*q + c_k)
= 2^k * m_coordinate.
```

This identity explains the algorithm and is not substituted into the
coordinate implementation.

## Reproduction

Runtime:

```text
Python 3.12.0
```

Exact command:

```sh
python3 -m unittest tests.test_landmark_coordinate -v
```

The required inputs are exactly `1, 3, 5, ..., 1999`. The stretch uses 1,000
values from Python's deterministic `random.Random` with seed `0xC011A7`, each
forced odd with `| 1`. All arithmetic uses exact Python integers.

COLLATZ_TAIL_0002_PASS
