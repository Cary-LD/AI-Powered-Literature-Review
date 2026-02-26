# Prompt: Ask Claude to Design Your Analysis Schema

Use this prompt at the start of Step 2 to have Claude design the classification system and LLM prompt for your specific review topic.

Getting this right is worth spending time on — it shapes the quality of every subsequent step.

---

## Prompt Template

```
I'm writing a literature review titled:

"[YOUR REVIEW TITLE]"

## My Zotero Library

- Total papers: approximately [N]
- Source: Zotero, stored at ~/Zotero/storage/, one subfolder per paper
- Main import sources: [e.g., Google Scholar, Web of Science, advisor recommendations]
- Research area: [brief description, e.g., materials science + machine learning]

## What I Need You to Do

1. **Design a classification system** (5–6 categories)
   - Should reflect the logical flow of the review (funnel structure: broad → narrow)
   - Each category should explain: what it includes, and its role in the review
   - Account for the fact that not all papers are "core" — include background and peripheral categories

2. **Design a JSON schema** for per-paper information extraction
   - Include: bibliographic fields, classification, research content, summary fields
   - Key fields: core_contribution, core_conclusion, review_angle
   - Include a field specifically for the technique/strategy addressing the review's core challenge

3. **Write a System Prompt** for a cheap LLM (Gemini Flash / GPT-4o-mini)
   - Clear classification system with concrete examples
   - Strict JSON output format
   - Explicit "do not fabricate" rule
   - Chinese for all descriptive fields (my review is in Chinese)

4. **Write a User Prompt template**
   - With placeholders for {filename} and {text}

## My Tentative Review Structure

[Describe your review structure here — the more detail the better. Example:]

- Chapter 1: Introduction, background
- Chapter 2: Traditional methods in [domain] and their limitations
- Chapter 3: Data-driven methods (general background)
- Chapter 4: Data-driven methods applied to [domain]
- Chapter 5: Strategies addressing [core challenge] (core chapter, structured by technique)
- Chapter 6: Trends and future directions
- Chapter 7: Conclusions

## Additional Requirements

- Classification categories should map to review chapters
- The `review_angle` JSON field should guide the writing LLM on where to place each paper in the review
- Include enough examples or description per category to prevent misclassification at category boundaries
```

---

## After Claude Gives You the Schema

Validate it:

1. Manually classify 5 papers you know well
2. Run the script on those 5 papers
3. If more than 2 mismatches: revise the system prompt
4. Pay special attention to the boundary between your "core" categories (D/E equivalent) — this is where most misclassification happens

Only after passing validation should you run the full batch.
