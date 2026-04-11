# 🌿 Green-Truth Auditor

**Instantly detect greenwashing and evaluate the true sustainability of any product or brand.**

Built for speed, transparency, and impact, the **Green-Truth Auditor** exposes misleading "eco-friendly" marketing fluff and rewards evidence-based sustainability claims using state-of-the-art LLM reasoning, RAG-lite verification, and a deterministic algorithmic Trust Breakdown.

---

## 🧠 How It Works: The Execution Pipeline

The Green-Truth Auditor isn't just a simple LLM wrapper. It uses a hybrid reasoning system:

1. **Extraction:** Evaluates text provided via direct input or scraped in real-time from a product URL using `trafilatura`.
2. **LLM Few-Shot Analysis:** The `gemini-2.5-flash` model parses the text to natively extract "Vague terms" (fluff) and "Strong terms" (certifications). It assigns a baseline categorization.
3. **RAG-Lite Verification:** We intercept the LLM output and check the raw text against our local `data/certifications.json` database. If the product claims "FSC" or "B-Corp", we verify that string natively and inject the official definition into the UI.
4. **Deterministic Scoring (SCORE_CONFIG):** We override the LLM's hallucinated scoring with a strict, transparent mathematical matrix. Points are rewarded for `Numbers` and `Certifications`, while heavily penalized for `Vague Claims` and `Lack of Evidence`.
5. **UI Rendering:** Streamlit visualizes the outcome in a beautiful 7-factor ✅/❌ grid, highlighting exactly which buzzwords triggered the algorithm.

---

## 🏗️ System Architecture

```mermaid
graph TD;
    A[User Input] -->|Direct Text| C[Streamlit Frontend]
    B[Product URL] -->|Trafilatura Scraper| C
    C --> D{LLM Engine}
    D --> E[Gemini 2.5 JSON Schema]
    D --> F[RAG-Lite JSON Database]
    E --> G{Compute Score Algorithm}
    F --> G
    G --> H[Final Trust Breakdown]
    H --> I[Dashboard & Visual Highlights]
```

---

## ✨ Key Features

- **Dual Input Modes:** Paste marketing copy directly or provide a URL (automatically scraped and parsed).
- **RAG-Lite Verification Engine:** We don't just rely on LLMs. The system actively cross-references text against a local database (`data/certifications.json`) of verified standards (like FSC, GOTS, B-Corp) to mathematically boost trust scores.
- **7-Factor Trust Breakdown:** A granular UI grid showing exactly *why* a product got its score, analyzing:
  - ✅ Certifications, Measurable Data, Supply Chain transparency, Third-Party Audits, and Lifecycle data.
  - ❌ Vague Claims (e.g., "planet-friendly") and Lack of Evidence.
- **Explainability First:** Highlights specific buzzwords in the parsed text and injects the verifiable definitions of found certifications directly into the results.
- **Hackathon Bulletproof:** Built-in fallback heuristics ensure the UI and demo stay perfectly functional even if API keys drop or rate limits engage.
- **Built-in Dataset Evaluation:** Includes `evaluate.py` to benchmark the engine strictly against 50 samples from the `Emanuse/greenwashing` HuggingFace dataset.

---

## 🚀 Quickstart

### 1. Installation
Clone the repo and install dependencies:
```bash
git clone https://github.com/Jagdish1123/Green-Truth-Auditor.git
cd Green-Truth-Auditor
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```
*(Note: If the key is missing or invalid, the app automatically drops into a smart offline demo mode!)*

### 3. Run the App
Launch the Streamlit dashboard:
```bash
streamlit run app.py
```

---

## 🔬 Dataset Evaluation Suite
Prove the architecture's accuracy by running the headless dataset evaluation tool. This script seamlessly downloads the `Emanuse/greenwashing` dataset and runs a 50-sample evaluation loop.

```bash
python evaluate.py
```
---

## 📓 Jupyter Notebook Implementation

The project includes a comprehensive Jupyter notebook (`green_truth_auditor.ipynb`) that demonstrates the step-by-step implementation of the Green-Truth Auditor. This notebook covers:

### Notebook Sections:
1. **Step 0 — Install Dependencies:** Installs all required Python libraries.
2. **Step 1 — Load & Train on the Greenwashing Dataset:** Loads the `Emanuse/greenwashing` dataset from Hugging Face, preprocesses the text, and trains a TF-IDF + Logistic Regression model for classifying marketing fluff vs. evidence-based claims.
3. **Step 2 — Buzzword Detection (Rule-Based Flag System):** Implements a rule-based system to detect vague greenwashing buzzwords and positive evidence signals.
4. **Step 3 — RAG: Certified Brand Database (B-Corp / GOTS):** Builds a FAISS-based semantic search index over certified brands for RAG verification.
5. **Step 4 — Input Interface: Text Box + URL Scraper:** Provides functions to scrape text from URLs and handle user input.
6. **Step 5 — AI Reasoning Summary Generator:** Generates human-readable explanations for audit results.
7. **Step 6 — Scoring Algorithm:** Implements the deterministic scoring system.
8. **Step 7 — Main Audit Function:** Combines all components into the main audit pipeline.
9. **Step 8 — Model Evaluation:** Evaluates the trained model on test data.
10. **Step 9 — Interactive Widget (Colab UI):** Provides an interactive Jupyter widget for testing the auditor.

### Running the Notebook:
1. Open the notebook in Jupyter Lab or Google Colab.
2. Run the cells in order from top to bottom.
3. The interactive widget at the end allows you to input product descriptions or URLs for auditing.

The notebook serves as both a development environment and a demonstration of the core algorithms.

---

## 🛠️ Built With & Tech Stack
* **Frontend/UI:** Streamlit
* **AI Engine:** Google Gemini (`gemini-2.5-flash`) via `google-genai`
* **Scraping:** Trafilatura
* **Data Sources / Testing:** `Emanuse/greenwashing` (Hugging Face Datasets)
* **Under the Hood:** Python, Pydantic, JSON Schema
