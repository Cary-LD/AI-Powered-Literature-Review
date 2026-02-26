# Step-by-Step Manual: From Zotero to a Literature Review

## Prerequisites

1. Zotero installed, papers stored in `~/Zotero/storage/` (one subfolder per paper)
2. OpenRouter API key (supports Gemini Flash and Claude)
3. Python dependencies:
   ```bash
   pip install pymupdf requests
   ```

---

## Step 1: Deduplicate Your Zotero Library

### Background
When importing papers from multiple sources, Zotero often creates duplicate entries. Each subfolder is named with an 8-character random string (e.g., `XXXXXXXX`) and contains one PDF.

### Method 1: Zotero Built-in Dedup (Recommended)
1. Open Zotero desktop
2. Click **Duplicate Items** in the left panel
3. Select all → right-click → **Merge items**
4. Re-sync; old folders are cleaned up

### Method 2: MD5 Hash Detection Script
See `step1_dedup/dedup_guide.md` for the full script.

### Notes
- Different Zotero folders may contain the same article (imported from multiple sources)
- Always merge inside Zotero — don't manually delete folders (breaks the database)

---

## Step 2: Design Your Analysis Schema

### 2.1 Ask Claude to Design the Classification System

Tell Claude your review topic and ask it to design:
1. A classification system for your literature (5–6 categories)
2. JSON fields to extract from each paper
3. A system prompt for Gemini Flash
4. A user prompt template

Use the template in `step2_template/claude_design_prompt.md`.

### 2.2 Classification System Design Principles

A good classification system for a literature review follows a **funnel structure**: from broad background to narrow core.

**Example structure:**
```
A. Traditional methods in [your domain]     → Chapter 2 (shows limitations)
B. Data-driven methods (general)            → Chapter 3 (methodological background)
C. Data-driven methods in [your domain]     → Chapter 4 (domain adoption)
D. Solutions to [your core problem] (general) → Chapter 5 (methodology)
E. Solutions to [your core problem] in [domain] → Chapter 5 (core papers)
F. Other / Unrelated
```

Categories D and E are your **core literature** — where most of the review's original contribution lies.

---

## Step 3: Batch Paper Analysis

### 3.1 Run the Analysis Script

```bash
cd ~/your/working/directory
export OPENROUTER_API_KEY="sk-or-..."

# Dry run: count papers without calling the API
python3 analyze.py --dry-run

# Test with 5 papers first
python3 analyze.py --limit 5

# Check output quality
cat ~/Zotero/storage/SOME_FOLDER/analysis.json

# Full run (700 papers ≈ 30–60 min)
python3 analyze.py
```

**Crash recovery:** The script skips folders that already have `analysis.json`. Just re-run after an interruption.

### 3.2 Aggregate Statistics

```bash
python3 summarize.py
```

Outputs category distribution, top methods, strategy counts, year distribution. Saves `summary.json`.

### 3.3 Quality Check

Spot-check 5 papers per category:
- Is `primary_category` correct?
- Is `core_contribution` accurate and specific?
- Is `relevance_score` calibrated (5 = must-cite, 1 = irrelevant)?
- Does `review_angle` give useful guidance on where/how to cite?

---

## Step 4: Generate the Review Outline

### 4.1 Run Cross-Analysis

```bash
python3 deep_analysis.py
```

Auto-generates:
- `review_outline.md`: section-by-section outline with paper lists
- `core_papers.json`: high-relevance papers (categories D+E) with full structured data
- `background_papers.json`: representative papers from categories A/B/C

### 4.2 Ask Claude to Write the Writing Brief

Send Claude:
1. Your review title and structure
2. Full `review_outline.md`
3. Category distribution statistics
4. Writing style requirements

Claude generates `TASK_FOR_WRITER.md` — a complete writing brief for the drafting LLM. See `step4_outline/claude_outline_prompt.md` for the prompt template.

---

## Step 5: Write the Review

### 5.1 Prepare Context for Claude

Send Claude:
1. `TASK_FOR_WRITER.md` (writing brief)
2. `review_outline.md` (outline)
3. `core_papers.json` (~200 core papers with structured data)
4. `background_papers.json` (~40 background papers)
5. `summary.json` (statistics for trend analysis chapter)

### 5.2 Writing Workflow

Ask Claude to first output **chapter-level argument summaries** (2–3 sentences per section), confirm the logic, then write the full text.

Recommended writing order:
1. Core chapter (heaviest, most original) — section by section
2. Background chapters
3. Introduction, trends, conclusion

### 5.3 Citation Format During Drafting

Use Zotero folder IDs as citation keys: `[XXXXXXXX]`

Advantages:
- Direct correspondence to PDF storage path
- Easy to find the source paper
- Replace with target journal format before submission

### 5.4 Output Files

- `review_draft.md`: full review text
- `references.md`: reference list organized by chapter/section

---

## FAQ

**Q: PDF text extraction fails?**
A: Scanned PDFs can't be text-extracted. The script records an `error` field in `analysis.json`. Skip or handle separately.

**Q: LLM classification is wrong?**
A: Delete that folder's `analysis.json` and re-run with `--folder FOLDER_NAME`. Or manually edit the JSON.

**Q: Context window too small for all paper data?**
A: `core_papers.json` can be ~300KB+. If it exceeds context, split by chapter.

**Q: Same paper appears in multiple folders?**
A: Pick one to cite (prefer the one with a more detailed `core_contribution`). List all duplicates in `TASK_FOR_WRITER.md` so the writing LLM knows which to skip.
