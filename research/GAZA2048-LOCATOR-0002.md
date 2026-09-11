# GAZA2048-LOCATOR-0002

This is a reproducible local synthetic comparison of a short visible QR locator and a larger QR payload. It makes no claim about printer/camera robustness.

## Method

`research/GAZA2048-LOCATOR-0002.py` uses Python `qrcode 8.2`, Pillow 12.3.0, OpenCV `QRCodeDetector` 5.0.0, and NumPy 2.5.3. QR uses ISO/IEC 18004-compatible byte-mode encoding, automatic version selection, 4-module quiet zone, box size 8, and error correction M. A contains 40 useful payload bits; B contains 160. Each payload includes `v1`, bit length, trial number, and base32 data, so exact recovery and wrong-but-decodable results are separate.

The fixed seed is 2048002, with 100 trials per payload/severity cell. Severity 0 is clean; 1 adds resampling and blur; 2 adds JPEG, rotation, contrast/noise; 3 adds perspective, crop/margin loss, and local occlusion. Clean controls are decoded before damaged cells are counted. The JSON result records exact settings and latency.

## Results

Run:

```sh
python3 research/GAZA2048-LOCATOR-0002.py
```

The generated `research/GAZA2048-LOCATOR-0002-results.json` is the machine-readable result. Recovery, wrong-decode rate, failures, QR version/module footprint, payload length, and median decode latency are recorded for every cell. The collision broker tests SHA-256 prefixes at 32/40/48 bits over 1,000/10,000/100,000 deterministic corpus items; a graph resolver must treat a collision as ambiguity and disambiguate using the full hash/content index, never as global uniqueness.

Observed summary (100 trials/cell): both clean controls passed. The 40-bit locator selected QR version 2 / 33 modules and recovered 98%, 98%, 99%, and 41% at severities 0–3. The 160-bit payload selected version 3 / 37 modules and recovered 98%, 97%, 98%, and 25%. Every cell had 0% undetected error; remaining trials were decode failures. The collision probe observed 0 collisions for each tested corpus/prefix pair, including 100,000 items at 32 bits. Median decode latency is retained per cell in the JSON output.

## Verdict

**REDESIGN** — the short locator is physically viable in this synthetic model, but the exact standard/representation and size need another bounded redesign before a print/phone experiment. This is a model result only; it does not establish physical robustness.

Smallest next experiment: use the measured short-QR module footprint and compare ECC-Q/H, a larger quiet zone, and a 48-bit locator under the same damage suite, then select the smallest representation that preserves clean-control and severe-cell performance. Keep full content addressing and collision resolution digital.
