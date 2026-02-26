# Reuse Guide: Adapting This Pipeline to Your Own Review Topic

This pipeline is topic-agnostic. Here's how to adapt it quickly.

---

## What You Need to Change

### 1. Classification System (Step 2)

The system prompt in `step2_template/system_prompt.md` uses a placeholder topic and generic A–F categories. Replace with your own:

**Design principles:**
- 5–6 categories, funnel structure (broad → narrow)
- Each category maps to a chapter in your review
- Must have "background" categories (A/B/C) and "core" categories (D/E)
- Provide concrete examples under each category — vague descriptions lead to misclassification

**Template:**
```
A. [Traditional methods in your domain]           → Chapter 2
B. [Foundational theory / general ML methods]     → Chapter 3
C. [Method applied to your domain]                → Chapter 4
D. [Solutions to your core problem (cross-domain)] → Chapter 5 (method level)
E. [Solutions to your core problem in your domain] → Chapter 5 (application level)
F. Other / Unrelated
```

### 2. `analyze.py` Configuration Block (Step 3)

```python
# Change these:
MODEL = "google/gemini-2.5-flash"       # model choice
ZOTERO_STORAGE = "~/Zotero/storage"    # usually unchanged
MAX_TEXT_CHARS = 30000                  # usually unchanged
```

### 3. `SYSTEM_PROMPT` in `analyze.py`

Replace the classification system and topic description. Keep these structural elements:
- Classification system with examples
- JSON output format (add/remove fields as needed)
- "Do not fabricate" rule
- Output language instruction

### 4. `normalize_strategy()` in `deep_analysis.py`

This function contains hardcoded strategy names for the original topic. Update the keyword mapping for your domain's specific terminology.

### 5. `TASK_FOR_WRITER.md` (Step 4)

This file is topic-specific and must be regenerated. Use the prompt in `step4_outline/claude_outline_prompt.md` with your own outline data.

---

## What You Don't Need to Change

- PDF extraction and API call logic in `analyze.py`
- Statistical logic in `summarize.py`
- Overall 5-step structure
- Framework of `deep_analysis.py` (only update the strategy normalization)

---

## Fastest Path to Adaptation

1. Describe your review topic to Claude → get a new System Prompt (~10 min)
2. Replace `SYSTEM_PROMPT` in `analyze.py`
3. Run 10 papers to validate, then full batch
4. Run `deep_analysis.py`, inspect generated outline
5. Send outline to Claude → generate `TASK_FOR_WRITER.md`
6. Send everything to Claude → draft the review

**Total setup time:** ~1 hour configuration + 30–60 min batch analysis + 30–60 min writing

---

## Extension Ideas

### Multi-round Analysis
After initial analysis, run a second pass on your highest-relevance papers (category E) with a more detailed prompt to extract finer-grained information (experiment parameters, quantitative results, etc.).

### Auto-generate Reference Format
Write a script that reads folder IDs from `references.md`, looks up corresponding Zotero entries, and outputs formatted citations (APA/IEEE/Vancouver).

### Better BibTeX Integration
If you use Zotero Better BibTeX, build a folder-name → BibTeX-key mapping for seamless citation format conversion.

### Multi-model Validation
For high-value papers (category E, score 5), run analysis with two different models and compare results as a confidence indicator.
