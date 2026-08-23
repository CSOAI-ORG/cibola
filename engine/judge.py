#!/usr/bin/env python3
"""CIBOLA deterministic judge — gold-label match, no LLM ever judges another LLM.
Returns PASS/FAIL/ERR; a model's answer is compared to the frozen gold class.
"""
import re

def judge(response: str, gold: str) -> str:
    """Compare a model answer against a frozen gold label (case-insensitive word match)."""
    if not response or response.startswith("ERR"):
        return "ERR"
    return "PASS" if re.search(rf"\b{re.escape(gold)}\b", response, re.I) else "FAIL"

def score(response: str, gold_list: list[str]) -> float:
    """Fraction of golds present in the response (for multi-class)."""
    if not response:
        return 0.0
    return sum(1 for g in gold_list if g.lower() in response.lower()) / len(gold_list)
