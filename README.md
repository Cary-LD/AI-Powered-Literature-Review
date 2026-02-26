# AI-Assisted Literature Review Pipeline

A **5-step pipeline** for writing academic literature reviews at scale — from a Zotero library to a publication-ready draft.

The workflow was designed by me and executed largely by [OpenClaw](https://github.com/openclaw/openclaw). Feeding this repo to OpenClaw with Claude Opus 4.6 should reproduce the full pipeline end-to-end.

## What This Does

Given a Zotero library of hundreds of papers, this pipeline:

1. **Deduplicates** the library
2. **Designs** a topic-specific classification schema (with AI assistance)
3. **Batch-analyzes** every paper using a cheap LLM (Gemini Flash)
4. **Synthesizes** a structured outline with cross-reference analysis
5. **Drafts** the full review using a capable LLM (Claude)

**Total cost:** ~$10 for 700+ papers. **Total time:** a few hours of compute + focused human review.

---

## Core Idea

```
You (Zotero library + instructions)
        ↓
OpenClaw (executes pipeline steps, writes scripts, coordinates models)
        ↓
OpenRouter API
        ├── Gemini Flash  → reads every paper → structured JSON per paper
        └── Claude Sonnet → reads all JSONs   → writes the review
```

Split the work by model capability:
- **Reading 700 papers** → cheap, parallelizable, tolerates ~10% error rate
- **Writing a coherent 15,000-word review** → needs a strong model, but only runs once

---

## Pipeline Overview

```
Step 1: Deduplicate
        Zotero storage folders → detect duplicate PDFs → clean up

Step 2: Design Analysis Schema (Claude via OpenClaw)
        Review topic → Claude designs JSON schema + classification system → configure analyze.py

Step 3: Batch Analysis (Gemini Flash via OpenRouter)
        N papers × PDF text → LLM → analysis.json per paper
        (~$0.002/paper, N=700 papers ≈ $1.5 total)

Step 4: Synthesize Outline (Claude via OpenClaw)
        All analysis.json → deep_analysis.py → review_outline.md
        Claude writes TASK_FOR_WRITER.md (detailed writing brief)

Step 5: Write the Review (Claude via OpenClaw)
        TASK_FOR_WRITER.md + outline + core paper data
        → Claude drafts → review_draft.md + references.md
```

---

## Directory Structure

```
zongshu_git/                      ← This repo (workflow documentation)
├── README.md                     ← This file
├── WORKFLOW.md                   ← Step-by-step manual
├── REUSE_GUIDE.md                ← How to adapt this to your own review topic
│
├── step1_dedup/
│   └── dedup_guide.md            ← Deduplication strategies
│
├── step2_template/
│   ├── analysis_json_schema.md   ← Full JSON schema spec
│   ├── system_prompt.md          ← LLM system prompt (with placeholder topic)
│   └── claude_design_prompt.md   ← Prompt to have Claude design your schema
│
├── step3_batch_analyze/
│   ├── analyze.py                ← Main batch analysis script
│   ├── summarize.py              ← Aggregation & statistics script
│   ├── example_analysis_output.json  ← Sample output
│   └── run_guide.md              ← How to run
│
├── step4_outline/
│   ├── deep_analysis.py          ← Cross-analysis + outline generation
│   ├── summary_json_guide.md     ← What summary.json contains
│   └── claude_outline_prompt.md  ← Prompt to generate the writing brief
│
└── step5_writing/
    └── writing_guide.md          ← Writing phase guide
```

---

## Actual Output Files (generated, not in this repo)

```
zotero_analyzer/           ← Your working directory (outside this repo)
├── analyze.py             ← Copied/adapted from step3
├── summarize.py
├── deep_analysis.py
├── summary.json           ← Aggregate stats (700+ papers)
├── core_papers.json       ← High-relevance paper data (for writing)
├── background_papers.json ← Background paper data
├── review_outline.md      ← AI-generated outline (human-reviewed)
├── TASK_FOR_WRITER.md     ← Detailed writing brief (for the writing LLM)
├── review_draft.md        ← Final review (~15,000 words)
└── references.md          ← Reference list organized by section
```

---

## Cost Breakdown

| Stage | Model | Volume | Cost |
|-------|-------|--------|------|
| Step 3: Batch analysis | Gemini 2.5 Flash | ~700 papers | ~$3 |
| Step 4–5: Outline + writing | Claude Sonnet | ~10 turns | ~$5–10 |
| **Total** | | | **~$10** |

---

## Dependencies

```bash
pip install pymupdf requests
```

- Python 3.9+
- [OpenClaw](https://github.com/openclaw/openclaw) (recommended for automated execution)
- OpenRouter API key (for both Gemini Flash and Claude)
- Zotero with local storage at `~/Zotero/storage/`

---

## Key Design Decisions

**Why Gemini Flash for batch analysis?**
At ~$0.004/paper, it's 5–10× cheaper than GPT-4o with ~85–90% classification accuracy — sufficient for information extraction tasks.

**Why store `analysis.json` per paper folder?**
Crash-safe incremental processing: re-running the script skips already-analyzed papers automatically.

**Why use folder IDs (e.g. `[XXXXXXXX]`) as citation keys during drafting?**
Direct correspondence to Zotero storage paths. Replace with proper citation format before submission.