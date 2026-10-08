# GAZA2048-COVER-CHANNEL-0003

## Verdict

**REDESIGN** — the standards-compatible artwork QR is viable and remains a graceful fallback, but this particular distributed RGB/chroma embedding loses all recovery at the harshest JPEG/color path. It does not justify a real cover/phone demo as an independent channel yet.

This is a local synthetic result only. It makes no claim about Amazon processing, printers, displays, or phone cameras.

## Reproduction

```sh
python3 research/GAZA2048-COVER-CHANNEL-0003.py
```

The experiment is deterministic (`SEED=920003`, 100 trials per construction/severity). It uses Python 3.12, `qrcode 8.2`, Pillow 12.3.0, OpenCV 5.0.0 and NumPy 2.5.3. The machine-readable output is `research/GAZA2048-COVER-CHANNEL-0003-results.json`; PNG demonstrations are in `research/GAZA2048-COVER-CHANNEL-0003-demo/`.

The locator carries 48 truncated SHA-256 bits plus a version and trial identifier in a short byte-mode QR payload. QR uses error correction M and a four-module quiet zone. The QR decoder is OpenCV `QRCodeDetector`; the chroma decoder is explicitly custom and is not claimed to be QR-compatible.

## Constructions and path

* **STANDARD:** ordinary QR placed on the deterministic cover.
* **ARTWORK:** the same module matrix, palette-matched dark/cream modules, framed and placed as cover ornament. It remains ordinary-QR decodable.
* **CHROMA:** 48 bits spread across 8×8 cover blocks as a low-amplitude blue-minus-red RGB modulation with a deterministic per-block bipolar pattern.
* **HYBRID:** ARTWORK plus CHROMA.

Each trial applies: RGB cover → resize thumbnail and back (severity 1+) → JPEG recompression (severity 2+, quality 48–82) → rotation ±6° → additive RGB noise → perspective warp and 3–13% margin/crop loss (severity 3). Severity 0 is clean. The clean-control gate passed at 100/100 for every construction.

## Results

Exact recovery rates; undetected QR errors were 0/100 in every cell. Intermediate severities are retained in the JSON.

| construction | QR-compatible | s0 | s1 | s2 | s3 | s3 QR / chroma components |
|---|---:|---:|---:|---:|---:|---:|
| standard | YES | 100% | 100% | 99% | 73% | 73% / — |
| artwork | YES | 100% | 100% | 100% | 76% | 76% / — |
| chroma | NO | 100% | 100% | 0% | 0% | — / 0% |
| hybrid | YES (fallback) | 100% | 100% | 100% | 76% | 76% / 0% |

The QR was version 2 / 33 modules. Median QR-observer latency was approximately 37–48 ms for standard/artwork/hybrid clean cells; the custom chroma construction’s median was approximately 100 ms clean and 70 ms at severity 3. The chroma perturbation proxy was mean absolute RGB delta 3.5, 95th percentile 7.0, with strength 7 per channel; it touched 75% of pixels because the spread-spectrum pattern is distributed. That footprint is not yet a convincing “invisible” result.

Desaturation/grayscale was tested on 50 severity-3 rows: 50/50 QR fallback rows remained classified as grayscale QR successes in the recorded sample, while the chroma-only channel has no grayscale recovery path. The full per-row evidence remains in the JSON.

## Wise Broker pass

I tested the adjacent opportunity of treating chroma as a fingerprint/error-check over the QR locator rather than as an independent locator. Under severity 3, hybrid recovery was 76%, exactly matching artwork QR recovery, while chroma contributed 0% additional recovery. Thus this embedding did not improve error detection or recovery over B; its only demonstrated role was clean-control redundancy and a potential future fingerprint channel.

## Failure cases and next experiment

The chroma channel survives resize/blur but fails after JPEG plus color/noise damage. The hybrid does not conceal this because its native QR remains the sole harsh-path survivor. The smallest justified next experiment is not a phone demo: compare a JPEG-aware low-frequency chroma codec with blockwise calibration/reference patches and 32/48 bits, keeping the same 100-trial path and requiring a clean-control gate. If it cannot beat artwork QR at severity 3 without materially increasing the RGB-distance proxy, stop and use a conventional visible QR.
