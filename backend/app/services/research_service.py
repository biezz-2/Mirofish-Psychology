"""
PRD: psychological data analysis + research question generation via LLM.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..utils.llm_client import LLMClient
from ..utils.locale import get_language_instruction
from ..utils.logger import get_logger

logger = get_logger("mirofish.research")


METHOD_PROMPTS = {
    "foq": "Focused Open Questions (terbuka, spesifik, netral, relevan).",
    "qualitative": "Pertanyaan kualitatif (wawancara mendalam / semi-terstruktur).",
    "quantitative": "Pertanyaan kuantitatif (skala Likert, pilihan ganda, rating).",
    "critical": "Pertanyaan kritis (analisis, sintesis, evaluasi).",
    "hypothetical": "Pertanyaan hipotetis (what if).",
    "comparative": "Pertanyaan komparatif (perbandingan).",
}


def _locale_instruction(locale: Optional[str]) -> str:
    if not locale:
        return get_language_instruction()
    loc = locale.lower()
    if loc == "id":
        return "Gunakan Bahasa Indonesia yang jelas dan profesional."
    return "Use clear, professional English."


class ResearchService:
    def __init__(self):
        self._llm = LLMClient()

    def analyze_psychology_data(
        self,
        payload: Dict[str, Any],
        *,
        locale: Optional[str] = None,
        template: str = "apa_psi",
    ) -> str:
        """Return markdown analysis (F-10–F-14)."""
        lang = _locale_instruction(locale)
        system = (
            "You are an expert psychology research assistant. "
            f"{lang}\n"
            "Produce structured Markdown: Executive summary, key insights, optional trends, recommendations.\n"
            f"Template hint: {template} (APA-style headings where appropriate)."
        )
        user = "Data (JSON):\n```json\n" + json.dumps(payload, ensure_ascii=False)[:120000] + "\n```"
        return self._llm.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.4,
            max_tokens=8192,
        )

    def generate_questions(
        self,
        payload: Dict[str, Any],
        methods: List[str],
        *,
        locale: Optional[str] = None,
        count_per_method: int = 5,
    ) -> Dict[str, Any]:
        """Return JSON dict method -> list of {question, rationale}."""
        lang = _locale_instruction(locale)
        method_desc = "\n".join(
            f"- {m}: {METHOD_PROMPTS.get(m, m)}" for m in methods
        )
        system = (
            "You output only valid JSON. Keys are method ids. "
            "Each value is an array of objects with keys question, rationale.\n"
            f"{lang}\n"
            f"Methods:\n{method_desc}\n"
            f"Generate up to {count_per_method} items per method."
        )
        user = "Context data:\n```json\n" + json.dumps(payload, ensure_ascii=False)[:80000] + "\n```"
        return self._llm.chat_json(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.7,
            max_tokens=8192,
        )
