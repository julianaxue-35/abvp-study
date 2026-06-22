"""
lib_catalog.py — ABVP Journal Catalog helpers
----------------------------------------------
Provides load_catalog, save_catalog, and validate_record for the
single-source-of-truth JSON catalog of journal abstracts + MCQs.
"""

import json
from pathlib import Path

# Repo root is one level up from this file (tools/ is directly under repo root).
_REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_KEYS = {
    "id", "title", "authors", "journal", "year", "citation",
    "doi", "source", "abstract", "abstract_origin",
    "domain", "subdomain_page", "mcqs",
}

VALID_SOURCES = {"folder", "discovered"}
YEAR_MIN, YEAR_MAX = 2021, 2026


def load_catalog(path: str) -> list:
    """Load the JSON catalog from *path* and return a list of record dicts.

    Returns an empty list if the file contains an empty JSON array.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_catalog(path: str, records: list) -> None:
    """Write *records* to *path* as pretty-printed JSON (2-space indent).

    Uses ensure_ascii=False so Unicode characters are preserved.
    Always writes a trailing newline.
    """
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def validate_record(rec: dict) -> list:
    """Validate a catalog record.

    Returns a list of human-readable problem strings.  An empty list
    means the record is valid.

    Rules
    -----
    * All required keys must be present.
    * ``year`` must be an int in [2021, 2026].
    * ``source`` must be one of {"folder", "discovered"}.
    * ``subdomain_page`` must be a relative path (e.g.
      "physical-health/surgery_anesthesia_hub.html") that exists under
      the repo root.
    * ``abstract`` must be a non-empty string.
    * Each entry in ``mcqs`` must be a dict with keys q, o, a, e where:
        - q is a non-empty string
        - o is a list of exactly 4 strings
        - a is an int with 0 <= a < 4
        - e is a non-empty string
    * Empty ``mcqs`` list is allowed (MCQs are populated in later tasks).
    * ``doi`` may be an empty string.
    """
    problems = []

    # --- Required keys ---
    missing = REQUIRED_KEYS - set(rec.keys())
    if missing:
        problems.append(f"Missing required keys: {sorted(missing)}")
        # Cannot check further fields that are missing; return early.
        return problems

    # --- year ---
    year = rec["year"]
    if not isinstance(year, int):
        problems.append(f"year must be an int, got {type(year).__name__!r}")
    elif not (YEAR_MIN <= year <= YEAR_MAX):
        problems.append(f"year {year} is outside allowed range {YEAR_MIN}–{YEAR_MAX}")

    # --- source ---
    if rec["source"] not in VALID_SOURCES:
        problems.append(
            f"source {rec['source']!r} is not one of {sorted(VALID_SOURCES)}"
        )

    # --- subdomain_page existence ---
    sp = rec["subdomain_page"]
    if not sp:
        problems.append("subdomain_page must not be empty")
    elif Path(sp).is_absolute():
        problems.append(f"subdomain_page {sp!r} must be a relative path, not absolute")
    else:
        full_path = (_REPO_ROOT / sp).resolve()
        if not full_path.is_relative_to(_REPO_ROOT):
            problems.append(f"subdomain_page {sp!r} escapes the repo root")
        elif not full_path.exists():
            problems.append(
                f"subdomain_page {sp!r} does not exist under repo root {_REPO_ROOT}"
            )

    # --- abstract ---
    if not isinstance(rec["abstract"], str) or not rec["abstract"].strip():
        problems.append("abstract must be a non-empty string")

    # --- mcqs ---
    mcqs = rec["mcqs"]
    if not isinstance(mcqs, list):
        problems.append("mcqs must be a list")
    else:
        for idx, mcq in enumerate(mcqs):
            prefix = f"mcqs[{idx}]"
            if not isinstance(mcq, dict):
                problems.append(f"{prefix}: must be a dict")
                continue
            # q
            q = mcq.get("q")
            if not isinstance(q, str) or not q.strip():
                problems.append(f"{prefix}: q must be a non-empty string")
            # o
            o = mcq.get("o")
            if not isinstance(o, list) or len(o) != 4:
                problems.append(f"{prefix}: o must be a list of exactly 4 strings")
            elif not all(isinstance(item, str) for item in o):
                problems.append(f"{prefix}: every element of o must be a string")
            # a
            a = mcq.get("a")
            if not isinstance(a, int) or not (0 <= a < 4):
                problems.append(f"{prefix}: a must be an int with 0 <= a < 4")
            # e
            e = mcq.get("e")
            if not isinstance(e, str) or not e.strip():
                problems.append(f"{prefix}: e must be a non-empty string")

    return problems
