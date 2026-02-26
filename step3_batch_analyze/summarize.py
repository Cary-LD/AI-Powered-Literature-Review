#!/usr/bin/env python3
"""
Aggregate all analysis.json files from Zotero storage.
Outputs a statistics report and saves summary.json.

Run after analyze.py has completed (or partially completed).
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

STORAGE = os.path.expanduser("~/Zotero/storage")


def normalize_category(cat):
    """Normalize 'C. Some label...' style strings to single letter A–F."""
    if not cat or not isinstance(cat, str):
        return "Unknown"
    c = cat.strip()[0].upper()
    if c in "ABCDEF":
        return c
    return "Unknown"


def load_all():
    results = []
    errors = []
    for folder in sorted(os.listdir(STORAGE)):
        fp = Path(STORAGE) / folder / "analysis.json"
        if fp.exists():
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["_folder"] = folder
                data["primary_category"] = normalize_category(data.get("primary_category"))
                if "secondary_categories" in data:
                    data["secondary_categories"] = [
                        normalize_category(c) for c in data.get("secondary_categories", [])
                    ]
                rs = data.get("relevance_score")
                if rs is not None:
                    try:
                        data["relevance_score"] = int(rs)
                    except (ValueError, TypeError):
                        data["relevance_score"] = 0
                results.append(data)
            except Exception as e:
                errors.append((folder, str(e)))
    return results, errors


def main():
    results, errors = load_all()
    print(f"{'='*60}")
    print(f"📊 Zotero Literature Analysis Summary")
    print(f"{'='*60}")
    print(f"\nLoaded: {len(results)} papers | Parse errors: {len(errors)}")

    if errors:
        print(f"\n⚠️ Failed to parse:")
        for folder, err in errors[:10]:
            print(f"  - {folder}: {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors)-10} more")

    # === 1. Primary Category Distribution ===
    primary = Counter()
    for r in results:
        cat = r.get("primary_category", "Unknown")
        primary[cat] = primary.get(cat, 0) + 1

    print(f"\n{'─'*60}")
    print(f"📂 1. Primary Category Distribution")
    print(f"{'─'*60}")
    cat_labels = {
        "A": "Traditional methods in domain",
        "B": "Data-driven methods (general background)",
        "C": "Data-driven methods in domain",
        "D": "Solutions to core challenge (any domain)",
        "E": "Solutions to core challenge in domain (core)",
        "F": "Other / Unrelated",
    }
    for cat in ["A", "B", "C", "D", "E", "F"]:
        count = primary.get(cat, 0)
        pct = count / len(results) * 100 if results else 0
        bar = "█" * int(pct / 2)
        label = cat_labels.get(cat, "")
        print(f"  {cat} ({label}): {count:>4} ({pct:5.1f}%) {bar}")
    for cat, count in primary.items():
        if cat not in ["A", "B", "C", "D", "E", "F"]:
            pct = count / len(results) * 100
            print(f"  {cat}: {count:>4} ({pct:5.1f}%)")

    # === 2. Relevance Score Distribution ===
    rel = Counter()
    for r in results:
        score = r.get("relevance_score", "?")
        rel[score] = rel.get(score, 0) + 1

    print(f"\n{'─'*60}")
    print(f"📈 2. Relevance Score Distribution (1–5)")
    print(f"{'─'*60}")
    for score in sorted(rel.keys(), key=lambda x: (isinstance(x, str), x)):
        count = rel[score]
        pct = count / len(results) * 100
        bar = "█" * int(pct / 2)
        print(f"  {score}: {count:>4} ({pct:5.1f}%) {bar}")

    # === 3. Secondary Category Distribution ===
    secondary = Counter()
    for r in results:
        for cat in r.get("secondary_categories", []):
            secondary[cat] += 1

    print(f"\n{'─'*60}")
    print(f"📂 3. Secondary Category Distribution (multi-select)")
    print(f"{'─'*60}")
    for cat in ["A", "B", "C", "D", "E", "F"]:
        count = secondary.get(cat, 0)
        print(f"  {cat}: {count:>4}")

    # === 4. Top ML Methods ===
    ml = Counter()
    for r in results:
        for m in r.get("ml_methods", []):
            if m:
                ml[m.strip()] += 1

    print(f"\n{'─'*60}")
    print(f"🤖 4. Top ML Methods (Top 20)")
    print(f"{'─'*60}")
    for method, count in ml.most_common(20):
        print(f"  {method}: {count}")

    # === 5. Top Core Techniques ===
    techniques = Counter()
    for r in results:
        for t in r.get("core_technique", []):
            if t:
                techniques[t.strip()] += 1

    print(f"\n{'─'*60}")
    print(f"🔧 5. Top Core Techniques (Top 20)")
    print(f"{'─'*60}")
    for technique, count in techniques.most_common(20):
        print(f"  {technique}: {count}")

    # === 6. Year Distribution ===
    years = Counter()
    for r in results:
        y = r.get("year")
        if y:
            years[y] += 1

    print(f"\n{'─'*60}")
    print(f"📅 6. Year Distribution")
    print(f"{'─'*60}")
    for y in sorted(years.keys()):
        count = years[y]
        bar = "█" * int(count / 2)
        print(f"  {y}: {count:>3} {bar}")

    # === 7. Language Distribution ===
    lang = Counter()
    for r in results:
        l = r.get("language", "Unknown")
        lang[l] += 1

    print(f"\n{'─'*60}")
    print(f"🌐 7. Language Distribution")
    print(f"{'─'*60}")
    for l, count in lang.most_common():
        print(f"  {l}: {count}")

    # === 8. Category × Relevance Crosstab ===
    print(f"\n{'─'*60}")
    print(f"📊 8. Category × Relevance Score Crosstab")
    print(f"{'─'*60}")
    cross = defaultdict(Counter)
    for r in results:
        cat = r.get("primary_category", "?")
        score = r.get("relevance_score", "?")
        cross[cat][score] += 1

    print(f"  {'Cat':<6}", end="")
    for s in [1, 2, 3, 4, 5]:
        print(f"  {s:>4}", end="")
    print(f"  {'Total':>6}")
    for cat in ["A", "B", "C", "D", "E", "F"]:
        row = cross.get(cat, {})
        total = sum(row.values())
        print(f"  {cat:<6}", end="")
        for s in [1, 2, 3, 4, 5]:
            print(f"  {row.get(s,0):>4}", end="")
        print(f"  {total:>6}")

    # === 9. Core Papers (Category E + score ≥ 4) ===
    core = [r for r in results
            if r.get("primary_category") == "E" and r.get("relevance_score", 0) >= 4]
    core.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    print(f"\n{'─'*60}")
    print(f"⭐ 9. Core Papers (Category E + score ≥ 4): {len(core)} papers")
    print(f"{'─'*60}")
    for r in core[:20]:
        title = r.get("title", "?")[:60]
        year = r.get("year", "?")
        score = r.get("relevance_score", "?")
        methods = ", ".join(r.get("ml_methods", [])[:3])
        print(f"  [{score}] {title}... ({year})")
        if methods:
            print(f"      Methods: {methods}")

    if len(core) > 20:
        print(f"  ... and {len(core)-20} more")

    # === Save summary.json ===
    summary = {
        "total": len(results),
        "parse_errors": len(errors),
        "primary_category_counts": dict(primary),
        "relevance_score_counts": {
            str(k): v for k, v in sorted(rel.items(), key=lambda x: (isinstance(x[0], str), str(x[0])))
        },
        "top_ml_methods": dict(ml.most_common(30)),
        "top_core_techniques": dict(techniques.most_common(30)),
        "year_distribution": {str(k): v for k, v in sorted(years.items())},
        "language_distribution": dict(lang),
    }
    out_path = os.path.join(os.path.dirname(__file__), "summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Summary saved to: {out_path}")


if __name__ == "__main__":
    main()
