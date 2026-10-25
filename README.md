# OpenAI — Corporate Development, Deal Lead (MIN-209)

**Application Package & Deterministic Verification Repository**

- **Role:** Corporate Development, Deal Lead
- **Company:** OpenAI (San Francisco, CA)
- **Posting URL:** [https://openai.com/careers/corporate-development-deal-lead-san-francisco/](https://openai.com/careers/corporate-development-deal-lead-san-francisco/)
- **Linear Issue:** `MIN-209` (`OpenAI — Corporate Development, Deal Lead (CV ready, awaiting tap)`)
- **Assigned Git Branch:** `minutta/min-209-openai-corporate-development-deal-lead-cv-ready-awaiting-tap`
- **Candidate:** Pavel Cherkashin (`pavel@mindrock.capital`)
- **Key Positioning Angle:** Venture investing as qualifying background; AI-native deal ops (sourcing intelligence, diligence, decision memos).

---

## 📁 Repository Structure

```
.
├── README.md                                     # This document
├── build_corpdev_cv.py                           # Deterministic ReportLab PDF + 300 DPI PNG generator
├── cv-pavel-cherkashin-corpdev.pdf               # Exact 1-page CV PDF (verified byte-for-byte)
├── cv-pavel-cherkashin-corpdev-hd.png            # 300 DPI High-Definition PNG render (2550x3300 px)
├── docs/
│   ├── APPLICATION_COVER_NOTE.md                 # Full executive cover note
│   ├── ONE_TAP_APPLICATION_CARD.md               # Summary action card for Principal Pavel Cherkashin
│   ├── OPENAI_CORPDEV_STRATEGY_BRIEF.md          # In-depth Corporate Development & M&A strategy
│   └── TAILORED_CV_OPENAI_CORPDEV.md             # Markdown version of the tailored CV
├── evidence/
│   ├── EVIDENCE.json                             # Machine-readable verification & audit metadata
│   └── MANIFEST.sha256                           # Cryptographic checksums of all deliverables
├── pyproject.toml                                # Project metadata and pinned dependencies
└── requirements.txt                              # Exact pinned render dependencies
```

---

## ⚙️ Building & Verifying

To reproduce the exact byte-for-byte PDF and 300 DPI PNG:

```bash
python3 build_corpdev_cv.py
```

Verification includes:
1. Exact 1-page PDF constraint (`page_count == 1`).
2. Programmatic PyMuPDF text block boundary checks (`out_of_bounds == 0`).
3. Pairwise bounding box collision detection (`collisions == 0`).
4. High-definition 300 DPI PNG export (2550 x 3300 px).
