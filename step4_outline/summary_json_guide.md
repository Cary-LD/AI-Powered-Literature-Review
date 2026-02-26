# summary.json Field Reference

`summarize.py` generates `summary.json` aggregating all `analysis.json` files.

## Structure

```json
{
  "total": 700,
  "parse_errors": 0,

  "primary_category_counts": {
    "A": 280,
    "B": 35,
    "C": 160,
    "D": 90,
    "E": 120,
    "F": 15
  },

  "relevance_score_counts": {
    "1": 15,
    "2": 20,
    "3": 100,
    "4": 450,
    "5": 115
  },

  "top_ml_methods": {
    "Neural Network / ANN": 80,
    "Deep Neural Network (DNN)": 55,
    "LSTM": 40,
    "...": "..."
  },

  "top_core_techniques": {
    "[Your main technique 1]": 60,
    "[Your main technique 2]": 30,
    "...": "..."
  },

  "year_distribution": {
    "2018": 45,
    "2019": 60,
    "2020": 80,
    "2021": 120,
    "2022": 130,
    "2023": 90,
    "2024": 75
  },

  "language_distribution": {
    "English": 650,
    "Chinese": 40,
    "Bilingual": 10
  }
}
```

## How Each Field Is Used

| Field | Used in |
|-------|---------|
| `total` | Chapter 1 intro (scope statement) |
| `primary_category_counts` | Scope and balance validation; Chapter 1 |
| `relevance_score_counts` | Quality check for batch analysis |
| `top_ml_methods` | Chapter 3 background, Chapter 5 methods |
| `top_core_techniques` | Chapter 5 section structure, Chapter 6 trends |
| `year_distribution` | Chapter 6 trend analysis (growth rate) |
| `language_distribution` | Chapter 1 scope (geographic coverage) |

## Notes

- `top_core_techniques` values are **raw strings** — not yet normalized through `normalize_technique()`
- `deep_analysis.py` applies `normalize_technique()` for proper grouping
- Use `deep_analysis.py` output (not `summary.json`) for Chapter 5 structure decisions
- Year distribution is useful for framing the "rapid growth" narrative in trend chapters

## Typical Category Distribution

As a sanity check, a well-balanced literature review typically shows:

| Category | Expected proportion |
|----------|-------------------|
| A (traditional) | 30–50% |
| B (ML background) | 5–10% |
| C (domain + ML) | 20–30% |
| D (core technique, general) | 10–15% |
| E (core, domain-specific) | 10–20% |
| F (unrelated) | <5% |

If your distribution is very different, check whether the classification system boundaries need adjustment.
