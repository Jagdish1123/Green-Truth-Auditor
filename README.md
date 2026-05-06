# Green-Truth Auditor

> Detects greenwashing in product marketing copy using ML classification, rule-based scoring, and semantic brand verification.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-semantic--search-blueviolet?style=flat-square)
![Jupyter](https://img.shields.io/badge/Jupyter-Colab--ready-F37626?style=flat-square&logo=jupyter)

---

## Problem

Brands use vague, unverifiable language ("eco-conscious", "planet-friendly", "natural") to signal sustainability without evidence. This tool audits product descriptions to distinguish substantiated claims from marketing fluff.

---

## Architecture

```
User Input
  ├── Text  ──────────────────────────────────────┐
  └── URL → BeautifulSoup scraper (≤5000 chars) ──┘
                          │
                  Preprocessing
          (lowercase · strip URLs · normalize)
                          │
         ┌────────────────┼────────────────┐
         │                │                │
  TF-IDF + LR       Regex engine      FAISS RAG
  Whole-text +       28 buzzword       Exact name +
  sentence-level     + evidence        semantic sim
  classification     patterns          25 brands
         │                │                │
         └────────────────┴────────────────┘
                          │
               Deterministic trust score (0–100)
               + points: certifications, measurable data
               − points: buzzwords, no evidence
                          │
               Verdict + Reasoning summary
```

---

## Tech Stack

| Component | Technology |
|---|---|
| ML model | TF-IDF + Logistic Regression (`scikit-learn`) |
| Semantic search | FAISS + `all-MiniLM-L6-v2` (`sentence-transformers`) |
| Web scraping | `requests` + `BeautifulSoup4` |
| Training data | HuggingFace `Emanuse/greenwashing` |
| Interactive UI | `ipywidgets` (Jupyter / Colab) |
| Runtime | Jupyter Lab / Google Colab |

> **Note:** Notebook-only project. No separate backend or web app — everything runs inside `green_truth_auditor.ipynb`.

---

## Key Engineering Decisions

- **Hybrid scoring, not pure ML.** ML contributes a label + confidence signal, but the final score is computed by an explicit deterministic formula — reproducible and auditable.
- **Two-pass RAG without a vector DB.** Exact brand name match runs first (high precision). FAISS semantic similarity is used only for non-exact matches, reducing false positives from drift on short product text.
- **Sentence-level classification.** Whole-text ML misses localized fluff. Each sentence is independently classified, giving a granular breakdown of which specific claims are problematic.
- **No external API dependency.** `generate_reasoning()` uses rule-based templates. Full pipeline runs offline after initial dataset download — no API keys required.
- **Scraper capped at 5000 chars.** Prevents context flooding from boilerplate-heavy product pages.

---

## Output Verdicts

| Score | Verdict |
|---|---|
| ≥ 70 | ✅ Legitimate — claims appear substantiated |
| 45–69 | ⚠️ Uncertain — partial evidence, needs scrutiny |
| < 45 | 🚩 Greenwashing — vague, unverifiable claims |

---

## How to Run

**Option A: Google Colab (recommended)**

1. Upload `green_truth_auditor.ipynb` to [colab.research.google.com](https://colab.research.google.com)
2. `Runtime → Run all`
3. Use the interactive widget in the final cell

**Option B: Local Jupyter**

```bash
pip install datasets sentence-transformers faiss-cpu scikit-learn \
            pandas numpy requests beautifulsoup4 transformers torch ipywidgets

jupyter lab green_truth_auditor.ipynb
```

No `.env` or API keys needed.

---

## Feature Coverage

| Feature | Status |
|---|---|
| Text + URL input | ✅ Done |
| Buzzword detection (28 regex patterns) | ✅ Done |
| ML classification (TF-IDF + LR) | ✅ Done |
| Sentence-level classification | ✅ Done |
| FAISS RAG over 25 certified brands | ✅ Done |
| Deterministic trust score (0–100) | ✅ Done |
| Rule-based reasoning summary | ✅ Done |
| Model evaluation on test split | ✅ Done |
| Interactive Colab widget | ✅ Done |
| LLM-generated reasoning | 🔜 Planned |
| Live B-Corp / GOTS registry lookup | 🔜 Planned |

---

## Limitations

| Limitation | Notes |
|---|---|
| JS-rendered pages | `requests` + BS4 can't execute JavaScript; React/Vue pages return empty |
| Static brand DB | 25 manually curated brands; no auto-sync with B-Corp or GOTS registries |
| Simple ML model | TF-IDF + LR won't catch nuanced or paraphrased greenwashing |
| Template reasoning | Rule-based summaries, not LLM-generated |
| English only | No multilingual support |
