# analysis.json Field Specification

Each paper analyzed by the LLM generates one `analysis.json` file, stored in its Zotero storage subfolder.

## Full JSON Structure

```json
{
  "title": "Paper title (original language, no translation)",
  "title_zh": "Chinese translation of title (or same as title if already Chinese)",
  "authors": ["First Author", "Second Author", "Third Author"],
  "year": 2023,
  "journal": "Journal or conference name",
  "language": "English / Chinese / Bilingual",

  "primary_category": "A",
  "secondary_categories": ["C", "D"],
  "relevance_score": 4,

  "domain_specific_material": "Specific material or domain object studied (null if N/A)",
  "research_problem": "Specific problem addressed by the paper (in Chinese)",
  "ml_methods": [
    "Method 1",
    "Method 2"
  ],
  "core_technique": [
    "Key technique or strategy 1",
    "Key technique or strategy 2"
  ],
  "dataset_info": "Brief description of dataset size and source (null if N/A)",

  "core_contribution": "1–2 sentences on the paper's main contribution (in Chinese)",
  "core_conclusion": "1–2 sentences on the main findings (in Chinese)",
  "limitations": "Limitations noted by authors or identified by you (in Chinese, null if none)",
  "review_angle": "Where and how to cite this paper in the review: which chapter/section, what argument it supports (in Chinese)",

  "keywords_zh": ["keyword1", "keyword2", "keyword3"],

  "_meta": {
    "input_tokens": 8736,
    "output_tokens": 512,
    "model": "google/gemini-2.5-flash",
    "analyzed_at": "2024-01-01 12:00:00"
  }
}
```

## Field Reference

### Bibliographic Fields

| Field | Type | Notes |
|-------|------|-------|
| `title` | string | Keep original language |
| `title_zh` | string | Chinese translation; if already Chinese, same as `title` |
| `authors` | array | First 3 authors only |
| `year` | int | Publication year; 0 if unknown |
| `journal` | string | Journal or conference name |
| `language` | string | English / Chinese / Bilingual |

### Classification

| Field | Type | Notes |
|-------|------|-------|
| `primary_category` | string | One letter from A–F (most representative) |
| `secondary_categories` | array | Additional applicable categories; can be empty |
| `relevance_score` | int | 1–5: 1=irrelevant, 5=core paper |

### Research Content

| Field | Type | Notes |
|-------|------|-------|
| `domain_specific_material` | string/null | Specific subject of study (material, dataset, system, etc.) |
| `research_problem` | string | Problem solved; in Chinese |
| `ml_methods` | array | ML/DL methods used; empty array if none |
| `core_technique` | array | Key techniques or strategies; empty array if none |
| `dataset_info` | string/null | Dataset scale and source; null if absent |

### Summary Fields (most important for writing)

| Field | Type | Notes |
|-------|------|-------|
| `core_contribution` | string | 1–2 sentences; in Chinese |
| `core_conclusion` | string | 1–2 sentences; in Chinese |
| `limitations` | string/null | In Chinese; null if none |
| `review_angle` | string | Chapter/section placement and argument support; in Chinese |
| `keywords_zh` | array | 3–6 Chinese keywords |

## Classification System

The A–F classification follows a **funnel structure** from broad background to narrow core.
**Replace the following with your actual topic when adapting this pipeline.**

### A. Traditional Methods in [Your Domain]
- Conventional experimental or simulation approaches
- **Review value:** Demonstrate cost, time, and scalability limitations → motivate data-driven approach

### B. Data-Driven Methods (General Background)
- Survey papers, foundational ML/DL methods
- Classic algorithms (GP, NN, RF, SVM, etc.) in relevant fields
- **Review value:** Establish methodological background and trends

### C. Data-Driven Methods Applied to [Your Domain]
- ML/DL applied to your domain (not necessarily addressing your core problem)
- **Review value:** Show that data-driven methods have entered your domain

### D. Solutions to [Your Core Problem] (Cross-domain)
- Methods addressing your core challenge in other domains
- **Review value:** Show transferable techniques

### E. Solutions to [Your Core Problem] in [Your Domain]
- Papers directly addressing your core challenge in your domain
- **Review value:** Core literature, primary source for the main chapter

### F. Other / Unrelated
- No clear connection to A–E

## relevance_score Rubric

| Score | Meaning | Typical case |
|-------|---------|-------------|
| 5 | Highly relevant, must-cite | Category E, directly addresses core challenge |
| 4 | High relevance | Strong category D/E papers |
| 3 | Moderate value | Category A/B/C background; D in other domains |
| 2 | Loosely related | Adjacent field, method not applicable |
| 1 | Essentially irrelevant | Category F, accidentally included |
