#!/usr/bin/env python3
"""
Cross-analysis + Review Outline Generation

Reads all analysis.json files, groups papers by technique/strategy,
and generates:
  - review_outline.md: structured outline with paper lists per section
  - core_papers.json: high-relevance papers (categories D+E) for writing
  - background_papers.json: representative A/B/C papers for background chapters

Before running:
  1. Update normalize_technique() with your domain's terminology
  2. Run after analyze.py and summarize.py have completed
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path

STORAGE = os.path.expanduser("~/Zotero/storage")
OUT_DIR = os.path.dirname(__file__)


def normalize_category(cat):
    if not cat or not isinstance(cat, str):
        return "Unknown"
    c = cat.strip()[0].upper()
    return c if c in "ABCDEF" else "Unknown"


def safe_int(v, default=0):
    try:
        return int(v)
    except Exception:
        return default


def load_all():
    results = []
    for folder in sorted(os.listdir(STORAGE)):
        fp = Path(STORAGE) / folder / "analysis.json"
        if fp.exists():
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["_folder"] = folder
                data["primary_category"] = normalize_category(data.get("primary_category"))
                data["relevance_score"] = safe_int(data.get("relevance_score"))
                data["year"] = safe_int(data.get("year"))
                if "secondary_categories" in data:
                    data["secondary_categories"] = [
                        normalize_category(c) for c in data.get("secondary_categories", [])
                    ]
                results.append(data)
            except Exception:
                pass
    return results


def normalize_method(m):
    """
    Merge synonymous ML method names.
    UPDATE THIS for your domain's specific terminology.
    """
    m = m.strip()
    mapping = {
        # Neural network variants
        "Artificial Neural Network": "Neural Network / ANN",
        "ANN": "Neural Network / ANN",
        "Deep Neural Network": "Deep Neural Network (DNN)",
        "DNN": "Deep Neural Network (DNN)",
        "Convolutional Neural Network": "Convolutional Neural Network (CNN)",
        "CNN": "Convolutional Neural Network (CNN)",
        "LSTM": "LSTM",
        "Long Short-Term Memory": "LSTM",
        "Physics-Informed Neural Network": "PINN",
        "PINN": "PINN",
        "Generative Adversarial Network": "GAN",
        "GAN": "GAN",
        # Classical ML
        "Support Vector Machine": "SVM / SVR",
        "SVM": "SVM / SVR",
        "SVR": "SVM / SVR",
        "Gaussian Process": "Gaussian Process (GP/GPR)",
        "Gaussian Process Regression": "Gaussian Process (GP/GPR)",
        "GPR": "Gaussian Process (GP/GPR)",
        "Random Forest": "Random Forest (RF)",
        "RF": "Random Forest (RF)",
        # Add your domain's common methods here
    }
    return mapping.get(m, m)


def normalize_technique(s):
    """
    Merge synonymous technique/strategy names using keyword matching.

    IMPORTANT: Update this function for your review topic.
    Replace the keyword lists below with the terminology used in your domain.

    Each block should:
    1. Define a canonical name (the string returned)
    2. List keywords that map to that canonical name
    """
    s = s.strip()
    sl = s.lower()

    # ── Example: Multi-fidelity data fusion ──
    if any(kw in sl for kw in ["multi-fidelity", "multifidelity", "multi fidelity",
                                 "dual fidelity", "bi-fidelity"]):
        return "Multi-Fidelity Data Fusion"

    # ── Example: Transfer learning ──
    if any(kw in sl for kw in ["transfer learn", "fine-tun", "fine tun"]):
        return "Transfer Learning"

    # ── Example: Physics-informed methods ──
    if any(kw in sl for kw in ["physics-inform", "physics inform", "pinn",
                                 "physics-guided", "physics constrain"]):
        return "Physics-Informed Methods / PINN"

    # ── Example: Surrogate modeling ──
    if any(kw in sl for kw in ["surrogate", "emulat", "metamodel"]):
        return "Surrogate Modeling"

    # ── Example: Data augmentation ──
    if any(kw in sl for kw in ["data augment"]):
        return "Data Augmentation"

    # ── Example: Virtual sample generation ──
    if any(kw in sl for kw in ["virtual sample", "synthetic sample", "synthetic data"]):
        return "Virtual Sample Generation"

    # ── Example: Active learning / adaptive sampling ──
    if any(kw in sl for kw in ["active learn", "adaptive sampling", "adaptive sample"]):
        return "Active Learning / Adaptive Sampling"

    # ── Example: Few-shot / small-data learning ──
    if any(kw in sl for kw in ["few-shot", "few shot", "small sample", "small data",
                                 "low-data", "low data"]):
        return "Few-Shot / Small-Data Learning"

    # ── Example: Sparse methods / compressed sensing ──
    if any(kw in sl for kw in ["sparse", "compress", "compressive"]):
        return "Sparse Methods / Compressed Sensing"

    # ── Example: Generative models ──
    if any(kw in sl for kw in ["gan", "generative adversarial", "variational autoencod",
                                 "diffusion model", "vae"]):
        return "Generative Models (GAN/VAE/Diffusion)"

    # ── Example: Multi-task learning ──
    if any(kw in sl for kw in ["multi-task", "multitask"]):
        return "Multi-Task Learning"

    # ── Example: Uncertainty quantification ──
    if any(kw in sl for kw in ["uncertainty", "bayesian", "probabilistic"]):
        return "Uncertainty Quantification / Bayesian Methods"

    # ── Add more mappings for your domain ──

    return s  # Return as-is if no match


def main():
    data = load_all()
    print(f"Loaded {len(data)} papers\n")

    # ── 1. Group by category ──
    by_cat = defaultdict(list)
    for r in data:
        by_cat[r["primary_category"]].append(r)

    # ── 2. Representative A/B/C papers ──
    background_reps = {}
    limits = {"A": 15, "B": 8, "C": 15}
    for cat in ["A", "B", "C"]:
        papers = by_cat.get(cat, [])
        papers_sorted = sorted(papers, key=lambda x: (x["relevance_score"], x["year"]), reverse=True)
        background_reps[cat] = papers_sorted[:limits[cat]]

    # ── 3. D+E papers grouped by technique ──
    de_papers = by_cat.get("D", []) + by_cat.get("E", [])

    technique_groups = defaultdict(list)
    for r in de_papers:
        techniques = r.get("core_technique", [])
        if not techniques:
            technique_groups["Other / Untagged"].append(r)
        else:
            primary_technique = normalize_technique(techniques[0])
            technique_groups[primary_technique].append(r)

    # ── 4. Method × Year trends (D+E) ──
    method_year = defaultdict(Counter)
    for r in de_papers:
        y = r.get("year", 0)
        if y < 2010:
            continue
        for m in r.get("ml_methods", []):
            nm = normalize_method(m)
            method_year[nm][y] += 1

    # ── 5. Technique × Year trends (D+E) ──
    technique_year = defaultdict(Counter)
    for r in de_papers:
        y = r.get("year", 0)
        if y < 2010:
            continue
        for t in r.get("core_technique", []):
            nt = normalize_technique(t)
            technique_year[nt][y] += 1

    # ── 6. Generate outline ──
    outline = []
    outline.append("=" * 80)
    outline.append("Review Outline: [YOUR REVIEW TITLE]")
    outline.append("=" * 80)
    outline.append("NOTE: Replace section titles and content guidance with your actual topic.\n")

    # Chapter 1: Introduction
    outline.append("─" * 80)
    outline.append("Chapter 1: Introduction")
    outline.append("─" * 80)
    outline.append("Purpose: Background, motivation, scope")
    outline.append("Suggested length: ~2 pages\n")
    outline.append("1.1 Importance of [your domain] and key challenges")
    outline.append("    → Cite A-category papers on limitations of traditional methods")
    outline.append("1.2 Rise of data-driven methods")
    outline.append("    → Cite B-category survey papers")
    outline.append("1.3 The core tension: [your challenge]")
    outline.append("    → Articulate the gap that this review addresses")
    outline.append("1.4 Scope and organization\n")

    # Chapter 2: Traditional methods
    outline.append("─" * 80)
    outline.append("Chapter 2: Traditional Methods and Their Limitations (Category A)")
    outline.append("─" * 80)
    outline.append("Purpose: Show why traditional approaches are insufficient")
    outline.append("Suggested length: ~3 pages\n")
    outline.append("2.1 [Traditional method type 1]")
    outline.append("2.2 [Traditional method type 2]")
    outline.append("2.3 Common limitations and bottlenecks\n")
    outline.append("Representative papers (Category A, Top 15):")
    for i, r in enumerate(background_reps.get("A", []), 1):
        title = r.get("title", "?")[:70]
        year = r.get("year", "?")
        score = r.get("relevance_score", "?")
        angle = r.get("review_angle", "")[:80]
        outline.append(f"  {i:2d}. [{score}] {title} ({year})")
        outline.append(f"      Folder: {r['_folder']}")
        if angle:
            outline.append(f"      Review angle: {angle}")

    # Chapter 3: Data-driven background
    outline.append("\n" + "─" * 80)
    outline.append("Chapter 3: Data-Driven Methods in [Your Field] (Category B)")
    outline.append("─" * 80)
    outline.append("Purpose: Establish methodological background")
    outline.append("Suggested length: ~2 pages\n")
    outline.append("3.1 Overview of ML/DL development in [field]")
    outline.append("3.2 Common methods (ANN, CNN, GP, RF, etc.)")
    outline.append("3.3 Opportunities and challenges\n")
    outline.append("Representative papers (Category B, Top 8):")
    for i, r in enumerate(background_reps.get("B", []), 1):
        title = r.get("title", "?")[:70]
        year = r.get("year", "?")
        score = r.get("relevance_score", "?")
        outline.append(f"  {i:2d}. [{score}] {title} ({year})")
        outline.append(f"      Folder: {r['_folder']}")

    # Chapter 4: Domain adoption
    outline.append("\n" + "─" * 80)
    outline.append("Chapter 4: Data-Driven Methods in [Your Domain] (Category C)")
    outline.append("─" * 80)
    outline.append("Purpose: Show data-driven methods are established in your domain")
    outline.append("Suggested length: ~3 pages\n")
    outline.append("4.1 [Application area 1]")
    outline.append("4.2 [Application area 2]")
    outline.append("4.3 [Application area 3]")
    outline.append("4.4 Persistent challenge: [your core problem]\n")
    outline.append("Representative papers (Category C, Top 15):")
    for i, r in enumerate(background_reps.get("C", []), 1):
        title = r.get("title", "?")[:70]
        year = r.get("year", "?")
        score = r.get("relevance_score", "?")
        methods = ", ".join(r.get("ml_methods", [])[:3])
        outline.append(f"  {i:2d}. [{score}] {title} ({year})")
        outline.append(f"      Folder: {r['_folder']}")
        if methods:
            outline.append(f"      Methods: {methods}")

    # Chapter 5: Core strategies
    outline.append("\n" + "─" * 80)
    outline.append("Chapter 5: Strategies for [Your Core Challenge] (Categories D+E) ★★★")
    outline.append("─" * 80)
    outline.append("Purpose: Core contribution — systematically survey all relevant strategies")
    outline.append("Suggested length: ~10–15 pages (largest chapter)\n")

    sorted_techniques = sorted(technique_groups.items(), key=lambda x: len(x[1]), reverse=True)

    section_num = 1
    for technique, papers in sorted_techniques:
        if len(papers) < 2:
            continue
        papers_sorted = sorted(papers, key=lambda x: (x["relevance_score"], x["year"]), reverse=True)
        e_count = sum(1 for p in papers if p["primary_category"] == "E")
        d_count = sum(1 for p in papers if p["primary_category"] == "D")

        outline.append(f"\n5.{section_num} {technique} ({len(papers)} papers: E={e_count}, D={d_count})")
        for i, r in enumerate(papers_sorted[:8], 1):
            title = r.get("title", "?")[:65]
            year = r.get("year", "?")
            cat = r.get("primary_category", "?")
            score = r.get("relevance_score", "?")
            contribution = r.get("core_contribution", "")[:80]
            outline.append(f"    {i}. [{cat}{score}] {title} ({year})")
            outline.append(f"       Folder: {r['_folder']}")
            if contribution:
                outline.append(f"       Contribution: {contribution}")
        if len(papers) > 8:
            outline.append(f"    ... {len(papers)-8} more papers")

        section_num += 1

    small_techniques = [(s, p) for s, p in sorted_techniques if len(p) < 2 and len(p) > 0]
    if small_techniques:
        outline.append(f"\n5.{section_num} Other Methods (1 paper each)")
        for technique, papers in small_techniques:
            r = papers[0]
            title = r.get("title", "?")[:65]
            year = r.get("year", "?")
            outline.append(f"    - {technique}: {title} ({year})")
            outline.append(f"      Folder: {r['_folder']}")

    # Chapter 6: Trends
    outline.append("\n" + "─" * 80)
    outline.append("Chapter 6: Trends and Future Directions")
    outline.append("─" * 80)
    outline.append("Purpose: Show temporal trends, identify future directions")
    outline.append("Suggested length: ~2–3 pages\n")

    outline.append("6.1 Method adoption trends (by year)")
    top_methods = sorted(method_year.items(), key=lambda x: sum(x[1].values()), reverse=True)[:8]
    for method, years in top_methods:
        year_str = ", ".join(f"{y}:{c}" for y, c in sorted(years.items()) if y >= 2017)
        outline.append(f"    {method}: {year_str}")

    outline.append("")
    outline.append("6.2 Strategy evolution trends (by year)")
    top_techs = sorted(technique_year.items(), key=lambda x: sum(x[1].values()), reverse=True)[:8]
    for tech, years in top_techs:
        year_str = ", ".join(f"{y}:{c}" for y, c in sorted(years.items()) if y >= 2017)
        outline.append(f"    {tech}: {year_str}")

    outline.append("")
    outline.append("6.3 Recommended future directions")
    outline.append("    - Multi-strategy combinations")
    outline.append("    - Foundation models / large language models in your domain")
    outline.append("    - Standardized benchmark datasets")
    outline.append("    - Uncertainty quantification and reliability")

    # Chapter 7: Conclusions
    outline.append("\n" + "─" * 80)
    outline.append("Chapter 7: Conclusions")
    outline.append("─" * 80)
    outline.append("Suggested length: ~1 page")

    # ── Write outline file ──
    outline_text = "\n".join(outline)
    outline_path = os.path.join(OUT_DIR, "review_outline.md")
    with open(outline_path, "w", encoding="utf-8") as f:
        f.write(outline_text)
    print(f"✅ Outline saved: {outline_path}")

    # ── Export D+E papers for writing ──
    de_export = []
    for r in de_papers:
        de_export.append({
            "folder": r["_folder"],
            "title": r.get("title", ""),
            "title_zh": r.get("title_zh", ""),
            "year": r.get("year"),
            "primary_category": r.get("primary_category"),
            "relevance_score": r.get("relevance_score"),
            "ml_methods": r.get("ml_methods", []),
            "core_technique": [normalize_technique(t) for t in r.get("core_technique", [])],
            "domain_specific_material": r.get("domain_specific_material"),
            "core_contribution": r.get("core_contribution", ""),
            "core_conclusion": r.get("core_conclusion", ""),
            "review_angle": r.get("review_angle", ""),
            "keywords_zh": r.get("keywords_zh", []),
        })
    de_export.sort(key=lambda x: (x["primary_category"], -x.get("relevance_score", 0)))

    de_path = os.path.join(OUT_DIR, "core_papers.json")
    with open(de_path, "w", encoding="utf-8") as f:
        json.dump(de_export, f, ensure_ascii=False, indent=2)
    print(f"✅ Core papers (D+E) saved: {de_path} ({len(de_export)} papers)")

    # ── Export A/B/C representative papers ──
    bg_export = {}
    for cat in ["A", "B", "C"]:
        bg_export[cat] = []
        for r in background_reps.get(cat, []):
            bg_export[cat].append({
                "folder": r["_folder"],
                "title": r.get("title", ""),
                "title_zh": r.get("title_zh", ""),
                "year": r.get("year"),
                "relevance_score": r.get("relevance_score"),
                "core_contribution": r.get("core_contribution", ""),
                "review_angle": r.get("review_angle", ""),
            })

    bg_path = os.path.join(OUT_DIR, "background_papers.json")
    with open(bg_path, "w", encoding="utf-8") as f:
        json.dump(bg_export, f, ensure_ascii=False, indent=2)
    print(f"✅ Background papers saved: {bg_path} "
          f"(A={len(bg_export['A'])}, B={len(bg_export['B'])}, C={len(bg_export['C'])})")

    # ── Print technique group statistics ──
    print(f"\n{'='*60}")
    print(f"📊 D+E Papers by Technique")
    print(f"{'='*60}")
    for technique, papers in sorted_techniques:
        e_count = sum(1 for p in papers if p["primary_category"] == "E")
        d_count = sum(1 for p in papers if p["primary_category"] == "D")
        print(f"  {technique}: {len(papers)} papers (E={e_count}, D={d_count})")

    print(f"\n{'='*60}")
    print(f"Generated files:")
    print(f"  1. review_outline.md       — outline with per-section paper lists")
    print(f"  2. core_papers.json        — D+E papers with full structured data")
    print(f"  3. background_papers.json  — A/B/C representative papers")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
