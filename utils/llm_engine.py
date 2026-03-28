import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types

# ─────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────

class AuditResult(BaseModel):
    classification: str
    buzzwords: List[str]
    strong_signals: List[str]
    score: int
    explanation: str

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

SCORE_CONFIG = {
    "base": 50,
    "vague_term_penalty": -6,
    "vague_term_cap": -30,
    "no_evidence_penalty": -20,
    "rag_cert_reward": 20,
    "rag_cert_cap": 45,
    "number_reward": 10,
    "supply_chain_reward": 8,
    "third_party_reward": 7,
    "lifecycle_reward": 5,
}

VAGUE_TERMS = [
    "eco-friendly", "green", "natural", "sustainable", "organic",
    "conscious", "planet-friendly", "environmentally friendly",
    "supports", "boosts", "enhances", "claims",
    "botanical", "scientifically formulated", "wellness",
    "pure", "clean", "safe for", "better for", "responsibly made"
]

CERT_TERMS = [
    "certifi", "gots", "fair trade", "ecocert", "fsc", "usda",
    "b-corp", "iso", "rainforest alliance", "oeko-tex"
]

SUPPLY_CHAIN_TERMS = ["ingredient", "material", "sourcing", "origin"]
LIFECYCLE_TERMS = ["carbon", "emissions", "lifecycle", "compostable"]
THIRD_PARTY_TERMS = ["third-party", "verified", "audited"]

# ─────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────

FEW_SHOT_PROMPT = """You are a Sustainability Auditor.

Classify:
- Marketing Fluff
- Partially Evidenced
- Evidence-Based

Rules:
- No data → Fluff
- Some signals → Partial
- Strong certs + data → Evidence-Based

Return JSON only:
{
  "classification": "...",
  "buzzwords": [...],
  "strong_signals": [...],
  "score": 0,
  "explanation": "..."
}

Text: {user_input}
"""

# ─────────────────────────────────────────────
# RAG
# ─────────────────────────────────────────────

def _load_cert_db():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "certifications.json")
        with open(path) as f:
            return json.load(f)
    except:
        return {}

def _rag_verify(text, db):
    tl = text.lower()
    return [f"{k}: {db[k]}" for k in db if k.lower() in tl]

# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────

def compute_score(text, result, verified):
    cfg = SCORE_CONFIG
    tl = text.lower()
    breakdown = {}

    vague_hits = sum(1 for t in VAGUE_TERMS if t in tl)
    breakdown["vague"] = max(vague_hits * cfg["vague_term_penalty"], cfg["vague_term_cap"])

    has_numbers = any(c.isdigit() for c in text)
    has_certs = bool(verified) or any(t in tl for t in CERT_TERMS)

    breakdown["no_evidence"] = cfg["no_evidence_penalty"] if not has_certs else 0
    breakdown["certs"] = min(len(verified) * cfg["rag_cert_reward"], cfg["rag_cert_cap"])
    breakdown["numbers"] = cfg["number_reward"] if has_numbers else 0
    breakdown["supply"] = cfg["supply_chain_reward"] if any(t in tl for t in SUPPLY_CHAIN_TERMS) else 0
    breakdown["third"] = cfg["third_party_reward"] if any(t in tl for t in THIRD_PARTY_TERMS) else 0
    breakdown["lifecycle"] = cfg["lifecycle_reward"] if any(t in tl for t in LIFECYCLE_TERMS) else 0

    score = cfg["base"] + sum(breakdown.values())
    return max(0, min(100, score)), breakdown

# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────

def _call_llm(text, key):
    client = genai.Client(api_key=key)
    prompt = FEW_SHOT_PROMPT.replace("{user_input}", text)
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AuditResult,
            ),
        )
        return json.loads(res.text)
    except:
        return None

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def analyze_text(text: str):
    key = os.getenv("GEMINI_API_KEY", "")
    tl = text.lower()

    # INSUFFICIENT DATA CHECK
    if not any(t in tl for t in VAGUE_TERMS + CERT_TERMS) and not any(c.isdigit() for c in text):
        return {
            "classification": "Insufficient Data",
            "buzzwords": [],
            "strong_signals": [],
            "score": 30,
            "trust_breakdown": {},
            "explanation": "No sustainability-related information found.",
        }

    result = _call_llm(text, key) if key and key != "your_api_key_here" else None

    if not result:
        result = {
            "classification": "Marketing Fluff",
            "buzzwords": [t for t in VAGUE_TERMS if t in tl][:5],
            "strong_signals": [],
            "explanation": "Fallback heuristic applied."
        }

    # RAG
    db = _load_cert_db()
    verified = _rag_verify(text, db)

    # CLEAN BUZZWORDS
    result["buzzwords"] = [w for w in result.get("buzzwords", []) if w.lower() in tl]

    # SCORE
    score, breakdown = compute_score(text, result, verified)

    # FINAL CLASSIFICATION
    if score >= 70:
        classification = "Evidence-Based"
    elif score >= 40:
        classification = "Partially Evidenced"
    else:
        classification = "Marketing Fluff"

    # EXPLANATION ALIGNMENT
    if classification == "Marketing Fluff":
        explanation = "Primarily vague claims with no strong verifiable evidence."
    elif classification == "Partially Evidenced":
        explanation = "Some verifiable elements exist but mixed with vague claims."
    else:
        explanation = "Strong certifications and measurable sustainability data present."

    if verified:
        explanation += f" Verified Certs: {', '.join([v.split(':')[0] for v in verified])}."

    return {
        "classification": classification,
        "buzzwords": result["buzzwords"],
        "strong_signals": verified,
        "score": score,
        "trust_breakdown": breakdown,
        "explanation": explanation,
    }
