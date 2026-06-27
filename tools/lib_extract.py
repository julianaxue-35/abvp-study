"""lib_extract.py — pure helpers for folder-article extraction & dedup."""
import re
from difflib import SequenceMatcher


def norm_title(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def find_cols(headers: list) -> dict:
    h = [str(c).strip().lower() if c is not None else "" for c in headers]
    cols = {}
    for i, name in enumerate(h):
        if not name:
            continue
        if "author" in name and "journal" in name:
            cols.setdefault("author", i)
            cols["combined_author_journal"] = True
            continue
        if "title" in name:
            cols.setdefault("title", i)
        elif "abstract" in name:
            cols.setdefault("abstract", i)
        elif "diplomate" in name:
            cols.setdefault("diplomate", i)
        elif "author" in name:
            cols.setdefault("author", i)
        elif "journal" in name and "year" not in name:
            cols.setdefault("journal", i)
        elif name == "year" or "article year" in name:
            cols.setdefault("year", i)
        elif "key" in name and ("point" in name or "takeaway" in name):
            cols.setdefault("keypoints", i)
        elif "takeaway" in name:
            cols.setdefault("keypoints", i)
    return cols


def detect_year(row: list, header_map: dict):
    yc = header_map.get("year")
    if yc is not None and yc < len(row) and row[yc] is not None:
        v = row[yc]
        if isinstance(v, (int, float)) and 1990 < v < 2030:
            return int(v)
        m = re.search(r"\b(20[0-2]\d)\b", str(v))
        if m:
            return int(m.group(1))
    for c in row:
        if isinstance(c, (int, float)) and 1990 < c < 2030:
            return int(c)
    for c in row:
        if isinstance(c, str):
            m = re.search(r"\b(20[0-2]\d)\b", c)
            if m:
                return int(m.group(1))
    return None


def author_lastname(authors: str) -> str:
    a = str(authors).strip()
    if not a:
        return ""
    first = re.split(r"[,;&]", a)[0].strip()
    return re.sub(r"[^a-z]", "", first.split()[-1].lower()) if first else ""


def is_dup(norm: str, author_last: str, year, existing: dict) -> bool:
    if norm in existing["titles"]:
        return True
    return (author_last, year) in existing["author_year"] and len(norm) > 12 and any(
        SequenceMatcher(None, norm, e).ratio() >= 0.90
        for e in existing["by_ay"].get((author_last, year), [])
    )


def fuzzy_matches(norm: str, existing_norms: list, lo=0.80, hi=0.99) -> list:
    out = []
    for e in existing_norms:
        r = SequenceMatcher(None, norm, e).ratio()
        if lo <= r < hi:
            out.append((e, round(r, 3)))
    return sorted(out, key=lambda x: -x[1])
