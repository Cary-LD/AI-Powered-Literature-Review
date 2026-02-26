# Prompt: Ask Claude to Write the Writing Brief

After `deep_analysis.py` generates `review_outline.md`, use this prompt to have Claude create a complete writing brief (`TASK_FOR_WRITER.md`) for the drafting LLM.

---

## Prompt Template

```
I have literature analysis data for a review paper and need you to write a complete
writing brief: TASK_FOR_WRITER.md.

## Review Information

- Title: "[YOUR REVIEW TITLE]"
- Language: [Chinese / English]
- Target word count: [15,000–20,000 words]
- Total papers analyzed: [N]
- Core papers (categories D+E): [N]

## Category Distribution

[Paste your summary.json primary_category_counts here, e.g.:]
- A (traditional methods): 280 papers
- B (ML background): 35 papers
- C (domain + ML): 160 papers
- D (core technique, general): 90 papers
- E (core, domain-specific): 120 papers

## Machine-Generated Outline

[Paste the FULL CONTENT of review_outline.md here]

## Requirements for TASK_FOR_WRITER.md

Include these sections:

1. **Review title and task overview**

2. **File locations** (which files the writing LLM needs to read)

3. **Classification system explanation** (A–F categories and their role in the review)

4. **Core requirements:**
   - Length and structure (per chapter)
   - Chapter 5 section structure (THIS IS CRITICAL — consolidate outline sections into
     8–12 final sections; merge any technique with fewer than [N] papers into "Other Methods")
   - Background chapters (concise, cite selectively)
   - Trends chapter guidance
   - Conclusion requirements (contributions summary / limitations / recommendations)
   - Writing style (avoid AI clichés: no "with the rapid development of...",
     no excessive bullet lists, no overuse of quotation marks)
   - Citation format (use folder IDs: [XXXXXXXX])

5. **Duplicate pairs list** (papers that appear in multiple folders; cite only the first)

6. **Invalid entries** (papers with year=0 or other metadata issues; do not cite)

7. **Output requirements** (where to save draft and references)

8. **Workflow suggestion** (writing order: core chapter first, then background, then framing)

## Special Instruction

For Chapter 5, YOU decide the consolidation:
- Which techniques have enough papers to warrant a standalone section? (suggest: ≥5 papers)
- Which should be merged into "Other Methods"?
- Final section titles and order (most-cited first)

[Paste the technique group statistics from deep_analysis.py output here]
```

---

## What a Good TASK_FOR_WRITER.md Looks Like

The writing brief should feel like a thorough editorial commission letter. It should:

1. **Give the LLM a complete picture** without it needing to make strategic decisions
2. **Specify Chapter 5 structure authoritatively** — this is the most important part
3. **Be specific about style** — academic writing quality varies enormously based on style guidance
4. **List all exceptions** — duplicate papers, invalid entries, special cases

A well-written brief means the drafting LLM can focus entirely on writing quality rather than organizational decisions.

---

## Chapter 5 Consolidation Principle

The machine-generated outline may have 15–20+ technique sections, many with only 1–2 papers. Consolidate to 8–12 sections:

- Any technique with ≥5 papers → standalone section
- Techniques with 2–4 papers → group into related sections
- Single-paper techniques → "Other Methods" section

Order sections by paper count (highest first). This ensures the most-studied techniques get the most coverage.

---

## Style Guidance Checklist for the Writing Brief

Include explicit prohibitions against these common AI writing patterns:

❌ "With the rapid development of X, more and more researchers have..."
❌ "In summary, it can be clearly seen that..."
❌ "First... Second... Third..." (excessive parallel structure)
❌ Every paragraph structured as a bullet list
❌ Excessive quotation marks for emphasis
❌ Abstract metaphors ("provides a powerful tool", "opens new pathways")

✅ Direct statement of research findings with citation support
✅ Logical paragraph-to-paragraph transitions
✅ Precise technical terminology
✅ Coherent argumentation, not just paper summaries
