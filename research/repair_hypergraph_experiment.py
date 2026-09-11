#!/usr/bin/env python3
"""Deterministic bounded hypergraph-learning experiment (stdlib only)."""
from __future__ import annotations
import itertools, json, random
from dataclasses import dataclass

N = 12
ALL = (1 << N) - 1

def bits(xs):
    out = 0
    for x in xs: out |= 1 << x
    return out

def subsets(mask):
    x = mask
    while True:
        yield x
        if x == 0: return
        x = (x - 1) & mask

def minimal_sets(family):
    fs = sorted(set(family), key=lambda x: (x.bit_count(), x))
    return tuple(x for x in fs if not any(y != x and y & x == y for y in fs))

def hitting_sets(edges):
    if not edges: return (0,)
    candidates = [0]
    for e in edges:
        candidates = [c | (1 << v) for c in candidates for v in range(N) if e & (1 << v)]
        candidates = list(set(candidates))
    return minimal_sets(candidates)

@dataclass
class Oracle:
    edges: tuple[int, ...]
    repairs_masking: tuple[int, ...] = ()
    queries: int = 0
    def __call__(self, s):
        self.queries += 1
        # Monotone systems fail when a bad edge is present. Adversarial systems
        # additionally contain explicit supersets that repair/mask failure.
        return not (any(e & s == e for e in self.edges) and
                    not any(r & s == r for r in self.repairs_masking))

def exact_edges(oracle):
    return minimal_sets([s for s in range(1, ALL + 1) if not oracle(s)])

def ddmin(oracle, failing):
    s = failing
    changed = True
    while changed:
        changed = False
        for v in range(N):
            if s & (1 << v) and not oracle(s ^ (1 << v)):
                s ^= 1 << v; changed = True
    return s

def learn(oracle, seed):
    rng = random.Random(seed)
    found = set()
    # Bounded adaptive probes: singleton screening, then random subsets and
    # delta-debugging of failures. This intentionally does not enumerate all 2^N.
    probes = [1 << i for i in range(N)]
    probes += [rng.randrange(1, ALL + 1) for _ in range(120)]
    for s in probes:
        if not oracle(s): found.add(ddmin(oracle, s))
    return tuple(sorted(found))

def f1(a, b):
    if not a: return 1.0
    return len(set(a) & set(b)) / len(set(a) | set(b))

def score(pred, truth):
    p, t = set(pred), set(truth)
    return {"exact": p == t, "precision": len(p & t) / len(p) if p else (1.0 if not t else 0.0),
            "recall": len(p & t) / len(t) if t else 1.0}

def make_systems():
    rng = random.Random(94001)
    systems = []
    for i in range(60):
        k = 1 + (i % 4)
        order = 1 + ((i * 7) % 4)
        edges = set()
        while len(edges) < k:
            edges.add(bits(rng.sample(range(N), order)))
        systems.append((f"mono-{i:02d}", tuple(sorted(edges)), ()))
    # Near-monotone corpus: explicit FAIL A / PASS B witness pairs.
    for i in range(12):
        e = bits(rng.sample(range(N), 2 + i % 3))
        repair = e | (1 << ((i + 5) % N))
        systems.append((f"adv-{i:02d}", (e,), (repair,)))
    return systems

def main():
    rows = []
    for idx, (name, edges, masks) in enumerate(make_systems()):
        ex = Oracle(edges, masks); truth = exact_edges(ex); exhaustive_q = ex.queries
        le = Oracle(edges, masks); pred = learn(le, 7000 + idx)
        repair_pred = hitting_sets(pred)
        gt_repairs = hitting_sets(truth)
        rows.append({"name": name, "kind": "adversarial" if masks else "monotone",
                     "edges": len(truth), "learner_edges": score(pred, truth),
                     "repairs": score(repair_pred, gt_repairs), "queries": le.queries,
                     "exhaustive_queries": exhaustive_q})
    mono = [r for r in rows if r["kind"] == "monotone"]
    adv = [r for r in rows if r["kind"] == "adversarial"]
    witnesses = 0
    for i, (_, edges, masks) in enumerate(make_systems()):
        if not masks: continue
        o = Oracle(edges, masks); seen = False
        for _ in range(30):
            a = random.Random(81000 + i).randrange(ALL + 1)
            b = a | (1 << random.Random(91000 + i).randrange(N))
            if not o(a) and o(b): seen = True; break
        witnesses += seen
    result = {"seed": 94001, "n_factors": N, "systems": rows,
              "summary": {"monotone_count": len(mono), "adversarial_count": len(adv),
                "monotone_edge_exact_rate": sum(r["learner_edges"]["exact"] for r in mono)/len(mono),
                "monotone_repair_exact_rate": sum(r["repairs"]["exact"] for r in mono)/len(mono),
                "mean_query_ratio_monotone": sum(r["queries"]/r["exhaustive_queries"] for r in mono)/len(mono),
                "adversarial_witness_detection_rate": witnesses/len(adv)}}
    print(json.dumps(result, sort_keys=True, indent=2))

if __name__ == "__main__": main()
