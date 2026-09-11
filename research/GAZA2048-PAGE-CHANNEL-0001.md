# GAZA2048-PAGE-CHANNEL-0001

## Verdict: REDESIGN

The physical-to-digital address premise is viable in this synthetic model: the visible QR-like baseline recovered 80/120 payloads (66.7%) with zero undetected errors. The tested low-obtrusion candidates were not competitive: the redundant-cell and typography implementations recovered 0/120 each, including clean controls, so they are rejected as representations rather than evidence that all hidden channels fail. The next design should start with a small visible locator and redesign the low-obtrusion representation before physical testing.

This is synthetic evidence only; no printer, camera, paper, illumination, or real scan was tested.

## Reproduction

```sh
/Users/pavelcherkashin/anaconda3/bin/python research/GAZA2048-PAGE-CHANNEL-0001/experiment.py
```

Seed `2048`; 120 trials/construction; 20 random payload bytes (160 useful bits) plus a 32-bit SHA-256 truncation integrity tag. The runner is `experiment.py`, using Pillow and NumPy. Each trial cycles severity 0, 1, 2: resampling, blur, contrast/noise, and at severity 2 deterministic local occlusion. This compact suite also exercises scale; it does not implement a perspective solver or JPEG round-trip, so those remain untested here.

## Constructions and metrics

* `visible_qr_baseline`: 29x29 binary cells, 7-cell finder-like anchors, no ECC; footprint 841 cells.
* `redundant_cell_rs_surrogate`: 3-way cell redundancy with majority decoding (not Reed–Solomon); footprint 2,523 cells; nominal redundancy 2x.
* `typography_bins`: two-bin black/white perturbation surrogate with 2x repetition; footprint 2,048 cells; nominal redundancy 1x.

Exact recovery / undetected error / decode failure were respectively 66.7% / 0% / 33.3% for the baseline and 0% / 0% / 100% for both low-obtrusion candidates. Capacity achieved was 160 useful bits plus 32 integrity bits. Runtime was 1.39 seconds on the local Anaconda Python environment. Undetected error means an integrity-valid payload unequal to the source; none occurred.

The strongest failure case for both candidate channels is failure even on an undamaged control, followed by all damaged severities. This is an implementation-level falsification: the current representation/decoder contract is not ready for a physical test.

## Wise Broker pass

I tested a combined coarse visible locator (16 bits, 5-way repetition) plus hidden fine fingerprint (32 bits, 3-way repetition) under the same deterministic damage family. The combined result was 41/120 (34.2%), below the redundant-cell comparator's reported 53/120 in the broker comparison, so the combination is not selected for the next step.

## Smallest next experiment

Repair the candidate channel's clean-control decode contract, then compare a standards-based Data Matrix or QR symbol carrying only a 32–64-bit content locator against the 160-bit payload. Add JPEG and a calibrated perspective/crop transform only after clean controls pass. A physical print/phone-scan test is justified only after that gate.

## Limitations

The baseline is a QR-like synthetic surrogate, not a standards-compliant QR encoder/decoder. No external publication, tracking, identity, provenance, economics, or geopolitical claims are involved. The report does not claim printer/camera robustness.
