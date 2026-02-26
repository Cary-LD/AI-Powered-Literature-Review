#!/usr/bin/env python3
"""
Zotero Batch Literature Analysis Tool

Reads every PDF in your Zotero storage directory, extracts text,
sends it to a cheap LLM (Gemini Flash by default), and saves
structured analysis.json files per paper.

Before running:
  1. Replace SYSTEM_PROMPT below with your topic-specific prompt
     (use step2_template/system_prompt.md as a template)
  2. Set your OPENROUTER_API_KEY environment variable
  3. Adjust config constants if needed
"""

import os
import sys
import json
import time
import glob
import argparse
import traceback
from pathlib import Path

import fitz  # pymupdf
import requests

# ──────────────────── Config ────────────────────

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-2.5-flash"          # Change to your preferred model
API_URL = "https://openrouter.ai/api/v1/chat/completions"
ZOTERO_STORAGE = os.path.expanduser("~/Zotero/storage")
OUTPUT_FILENAME = "analysis.json"

MAX_TEXT_CHARS = 30000       # Max characters extracted per PDF (~7,500 tokens)
MAX_RETRIES = 3
RETRY_DELAY = 5              # seconds
CONCURRENCY = 5              # concurrent requests (currently unused; serial by default)
RATE_LIMIT_DELAY = 0.5       # seconds between requests (increase if you hit 429s)

# ──────────────────── Prompts ────────────────────
# IMPORTANT: Replace this with your topic-specific system prompt.
# Use step2_template/system_prompt.md as a starting point.
# Ask Claude to generate a prompt tailored to your review topic
# using step2_template/claude_design_prompt.md.

SYSTEM_PROMPT = """You are a senior researcher in [YOUR RESEARCH DOMAIN], preparing literature \
for a review paper titled "[YOUR REVIEW TITLE]".

Your task is to read the full text of an academic paper and extract structured information. \
Follow the output format exactly.

## Classification System

Classify the paper into one of the following categories (multiple allowed):

**A. Traditional Methods in [Your Domain]**
- [Describe: e.g., experimental methods, simulation, conventional modeling]
- Value: demonstrates limitations → motivates data-driven approach

**B. Data-Driven Methods (General Background)**
- [Describe: e.g., ML/DL surveys, foundational algorithms in your field]
- Value: establishes methodological background

**C. Data-Driven Methods Applied to [Your Domain]**
- [Describe: ML/DL applied to your domain, not necessarily addressing the core challenge]
- Value: shows data-driven methods have entered your domain

**D. Solutions to [Your Core Challenge] (Any Domain)**
- [Describe: e.g., transfer learning, data augmentation, physics-informed methods, etc.]
- Value: cross-domain techniques transferable to your problem

**E. Solutions to [Your Core Challenge] in [Your Domain]**
- [Describe: papers directly addressing your core challenge within your domain]
- Value: core literature

**F. Other / Unrelated**
- No clear connection to the above

## Output Requirements

Output a single JSON object only (no other text):

```json
{
  "title": "Paper title (original language)",
  "title_zh": "Chinese translation (if already Chinese, same as title)",
  "authors": ["First Author", "Second Author"],
  "year": 2023,
  "journal": "Journal or conference name",
  "language": "English/Chinese/Bilingual",

  "primary_category": "Most applicable category from A–F",
  "secondary_categories": ["Other applicable categories, or empty array"],
  "relevance_score": 4,

  "domain_specific_material": "Specific material/system studied, or null",
  "research_problem": "Problem addressed (in Chinese)",
  "ml_methods": ["ML/DL methods used, or empty array"],
  "core_technique": ["Key techniques for the core challenge, or empty array"],
  "dataset_info": "Dataset size and source, or null",

  "core_contribution": "1–2 sentence main contribution (in Chinese)",
  "core_conclusion": "1–2 sentence main findings (in Chinese)",
  "limitations": "Limitations (in Chinese), or null",
  "review_angle": "Where and how to cite in the review: chapter, section, argument (in Chinese)",

  "keywords_zh": ["3–6 Chinese keywords"]
}
```

## Rules

1. All descriptive fields must be in Chinese
2. relevance_score: 1=irrelevant, 2=loosely related, 3=some value, 4=high relevance, 5=core paper
3. If unrelated: primary_category=F, relevance_score=1
4. Do not fabricate — use null for anything not in the text
5. List only the first 3 authors
6. If PDF text is incomplete, note it in core_contribution"""

USER_PROMPT_TEMPLATE = """Please analyze the following academic paper and extract structured information.

Filename: {filename}

===== PAPER TEXT =====
{text}
===== END OF TEXT =====

Output strictly in JSON format as specified. No other text."""

# ──────────────────── Core Functions ────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF, capped at MAX_TEXT_CHARS."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
            if len(text) > MAX_TEXT_CHARS:
                text = text[:MAX_TEXT_CHARS]
                text += "\n\n[Text truncated — above is the first portion]"
                break
        doc.close()
        return text.strip()
    except Exception as e:
        return f"[PDF text extraction failed: {str(e)}]"


def call_llm(text: str, filename: str) -> dict:
    """Send paper text to LLM and return parsed JSON result."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",  # Optional: update with your repo
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                filename=filename, text=text
            )},
        ],
        "temperature": 0.1,   # Low temperature for consistent extraction
        "max_tokens": 2000,
        "response_format": {"type": "json_object"},
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)

            if resp.status_code == 429:
                wait = RETRY_DELAY * (attempt + 2)
                print(f"  ⏳ Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()

            content = data["choices"][0]["message"]["content"]
            # Strip markdown code block if present
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)

            # Record token usage
            usage = data.get("usage", {})
            result["_meta"] = {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "model": MODEL,
                "analyzed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            return result

        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parse error (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ API request failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        except (KeyError, IndexError) as e:
            print(f"  ⚠️ Unexpected response format (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    return {"error": f"Failed after {MAX_RETRIES} attempts", "filename": filename}


def process_one(folder_path: str) -> dict:
    """Process one Zotero storage folder."""
    folder_name = os.path.basename(folder_path)
    output_path = os.path.join(folder_path, OUTPUT_FILENAME)

    # Skip if already processed
    if os.path.exists(output_path):
        return {"status": "skipped", "folder": folder_name}

    # Find PDF
    pdfs = glob.glob(os.path.join(folder_path, "*.pdf"))
    if not pdfs:
        return {"status": "no_pdf", "folder": folder_name}

    pdf_path = pdfs[0]
    filename = os.path.basename(pdf_path)

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if len(text) < 100:
        result = {
            "error": "Extracted text too short — likely a scanned PDF",
            "filename": filename,
            "extracted_chars": len(text),
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return {"status": "too_short", "folder": folder_name, "chars": len(text)}

    # Call LLM
    result = call_llm(text, filename)

    # Save result
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    status = "error" if "error" in result else "success"
    return {"status": status, "folder": folder_name, "filename": filename}


# ──────────────────── Main ────────────────────

def main():
    parser = argparse.ArgumentParser(description="Batch analyze Zotero library")
    parser.add_argument("--dry-run", action="store_true", help="Count only, no API calls")
    parser.add_argument("--limit", type=int, default=0, help="Max papers to process (0=all)")
    parser.add_argument("--concurrency", type=int, default=CONCURRENCY)
    parser.add_argument("--folder", type=str, default="", help="Process only this folder")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("❌ Set environment variable OPENROUTER_API_KEY first")
        sys.exit(1)

    # Collect folders
    if args.folder:
        folders = [os.path.join(ZOTERO_STORAGE, args.folder)]
    else:
        folders = sorted([
            os.path.join(ZOTERO_STORAGE, d)
            for d in os.listdir(ZOTERO_STORAGE)
            if os.path.isdir(os.path.join(ZOTERO_STORAGE, d))
        ])

    # Stats
    total = len(folders)
    has_pdf = sum(1 for f in folders if glob.glob(os.path.join(f, "*.pdf")))
    already_done = sum(1 for f in folders if os.path.exists(os.path.join(f, OUTPUT_FILENAME)))
    to_process = has_pdf - already_done

    print(f"📊 Summary:")
    print(f"   Total folders: {total}")
    print(f"   With PDF: {has_pdf}")
    print(f"   Already analyzed: {already_done}")
    print(f"   To process: {to_process}")
    print()

    if args.dry_run:
        print("🏃 Dry run — no API calls made")
        return

    if to_process == 0:
        print("✅ All papers already analyzed")
        return

    limit = args.limit if args.limit > 0 else to_process
    print(f"🚀 Starting (limit={limit}, rate_limit_delay={RATE_LIMIT_DELAY}s)")
    print()

    stats = {"success": 0, "skipped": 0, "no_pdf": 0, "too_short": 0, "error": 0}
    start_time = time.time()

    pending_folders = [
        f for f in folders
        if glob.glob(os.path.join(f, "*.pdf"))
        and not os.path.exists(os.path.join(f, OUTPUT_FILENAME))
    ][:limit]

    for i, folder in enumerate(pending_folders, 1):
        folder_name = os.path.basename(folder)
        pdfs = glob.glob(os.path.join(folder, "*.pdf"))
        pdf_name = os.path.basename(pdfs[0]) if pdfs else "?"

        elapsed = time.time() - start_time
        rate = i / elapsed if elapsed > 0 else 0
        eta = (len(pending_folders) - i) / rate if rate > 0 else 0

        print(f"[{i}/{len(pending_folders)}] {pdf_name[:70]}...")

        result = process_one(folder)
        stats[result["status"]] = stats.get(result["status"], 0) + 1

        if result["status"] == "success":
            print(f"  ✅ Done")
        elif result["status"] == "error":
            print(f"  ❌ Failed")
        elif result["status"] == "too_short":
            print(f"  ⚠️ Text too short ({result.get('chars', '?')} chars) — likely scanned PDF")

        if i % 10 == 0:
            print(f"\n📈 Progress: {i}/{len(pending_folders)} | "
                  f"success={stats['success']} error={stats['error']} short={stats['too_short']} | "
                  f"ETA: {eta/60:.1f} min\n")

        time.sleep(RATE_LIMIT_DELAY)

    total_time = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"🏁 Done!")
    print(f"   Time: {total_time/60:.1f} min")
    print(f"   Success: {stats['success']}")
    print(f"   Skipped: {stats['skipped']}")
    print(f"   No PDF: {stats['no_pdf']}")
    print(f"   Too short: {stats['too_short']}")
    print(f"   Failed: {stats['error']}")


if __name__ == "__main__":
    main()
