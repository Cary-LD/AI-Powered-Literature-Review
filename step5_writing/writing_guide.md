# Step 5: Writing the Review with Claude

## Prerequisites

Confirm these files are ready:
- `TASK_FOR_WRITER.md` — writing brief
- `review_outline.md` — outline
- `core_papers.json` — high-relevance papers (categories D+E)
- `background_papers.json` — background papers (categories A/B/C)
- `summary.json` — aggregate statistics

## Model Recommendation

Use **Claude Sonnet** (or equivalent capable model):
- Supports 100K+ context (handles all data files)
- Strong academic writing quality
- Supports long output

## Prompt

```
Please read the following files and write the review:

1. TASK_FOR_WRITER.md (writing brief — read this first)
2. review_outline.md (outline)
3. core_papers.json (core literature data, categories D+E)
4. background_papers.json (background papers)
5. summary.json (statistics for trend analysis chapter)

First output a chapter-level argument summary (2–3 sentences per section).
After confirmation, write the full draft.

Save the draft to: review_draft.md
Save the reference list to: references.md
```

## Quality Control Checklist

### Citation format

All citations should use folder IDs: `[XXXXXXXX]`

❌ Wrong: (Smith et al., 2023)
✅ Right: [XXXXXXXX]

### No duplicate citations

Check that the same paper isn't cited under two different folder IDs.
Cross-reference with the duplicate pairs list in `TASK_FOR_WRITER.md`.

### Invalid entries not cited

Verify that any entries marked as invalid in `TASK_FOR_WRITER.md` (year=0, non-paper entries) are not cited.

### Word count check

```bash
wc -w review_draft.md
```

For Chinese text: `wc -w` counts spaces, not characters. Divide by ~0.6 for approximate character count.
Target: 15,000–20,000 Chinese characters (or your specified target).

### Chapter 5 structure

Verify Chapter 5 follows the 8–12 section structure from `TASK_FOR_WRITER.md`, not the raw machine-generated outline (which may have had more sections).

### Chapter 5 proportion

Chapter 5 (core chapter) should be ~50–60% of total length.

### Writing style

Check for common AI writing patterns to avoid:

❌ "With the rapid development of X, more and more researchers..."
❌ "In summary, it can be clearly seen that..."
❌ Excessive parallel "First / Second / Third" structures
❌ Paragraphs that are just bulleted paper summaries
❌ Overuse of quotation marks for emphasis
❌ Abstract metaphors ("opens new pathways", "powerful tool")

✅ Direct statements with citation support
✅ Paragraph-level logical flow
✅ Precise technical language
✅ Actual synthesis, not just description

## Reference List Format

`references.md` should organize citations by chapter/section:

```markdown
## Chapter 2 References

[XXXXXXXX] Title of paper. Journal Name, Year.
[YYYYYYYY] Title of paper. Journal Name, Year.

## Chapter 3 References

[ZZZZZZZZ] Title of paper. Journal Name, Year.

## Chapter 5 References

### 5.1 [Section Title]

[AAAAAAAA] Title. Journal, Year.
[BBBBBBBB] Title. Journal, Year.
```

## Post-Draft Processing

### Before submission

1. **Replace folder IDs with proper citation format**

   Write a script that maps folder IDs to Zotero entries and outputs your target format:
   ```python
   # Read references.md → build ID-to-citation mapping
   # Globally replace in review_draft.md
   ```

2. **Verify all cited papers exist in Zotero**

3. **Adjust formatting for target journal**
   (word count limits, heading levels, figure/table requirements)

### Version management

```
review_draft_v1.md   ← First draft from Claude
review_draft_v2.md   ← After first revision
review_draft_v3.md   ← Pre-submission final
```

## Iterative Refinement

For multi-pass improvement:

1. **First pass:** Generate full draft
2. **Second pass:** Identify weak sections (poor logic, thin citation support)
3. **Third pass:** Rewrite weak sections with more specific paper data
4. **Final pass:** Style and consistency check

When refining specific sections, provide:
- The current section text
- The relevant paper data from `core_papers.json`
- Specific critique (logic gap, missing citation, awkward phrasing)
