# Step 3: Running the Batch Analysis

## Environment Setup

```bash
# Install dependencies
pip install pymupdf requests

# Set API key (OpenRouter supports Gemini Flash and Claude)
export OPENROUTER_API_KEY="sk-or-your-key-here"

# Verify Zotero storage path (macOS default)
ls ~/Zotero/storage | head -10
```

## Configuration

Open `analyze.py` and update the top section:

```python
MODEL = "google/gemini-2.5-flash"               # Model choice (see table below)
ZOTERO_STORAGE = os.path.expanduser("~/Zotero/storage")  # Storage path
MAX_TEXT_CHARS = 30000                           # PDF text extraction limit
RATE_LIMIT_DELAY = 0.5                          # Seconds between requests
```

**Also replace `SYSTEM_PROMPT`** with your topic-specific prompt from Step 2.

### Model Selection

| Model | Cost/paper | Speed | Accuracy | Notes |
|-------|-----------|-------|----------|-------|
| google/gemini-2.5-flash | ~$0.002 | Fast | 85–90% | Default |
| google/gemini-2.0-flash | ~$0.001 | Very fast | 80–85% | Budget option |
| anthropic/claude-3-5-haiku | ~$0.003 | Medium | 88–92% | Higher accuracy |
| openai/gpt-4o-mini | ~$0.003 | Fast | 88–90% | Alternative |

## Running

### Phase 1: Dry Run (Required)

```bash
# Count papers without API calls
python3 analyze.py --dry-run
```

### Phase 2: Small Batch Validation (Required)

```bash
# Test with 5 papers
python3 analyze.py --limit 5

# Inspect output
cat ~/Zotero/storage/$(ls ~/Zotero/storage | head -1)/analysis.json | python3 -m json.tool
```

**Validation checklist:**
- [ ] `primary_category` assignment is correct?
- [ ] `core_contribution` accurately captures the main work?
- [ ] `core_technique` correctly identifies the key method?
- [ ] `relevance_score` is well-calibrated (5=must-cite, 1=irrelevant)?
- [ ] `review_angle` gives useful citation guidance?
- [ ] JSON is valid (no parse errors)?

If more than 2 out of 5 are wrong, revise `SYSTEM_PROMPT` and retry.

### Phase 3: Medium Batch Test

```bash
python3 analyze.py --limit 50
python3 summarize.py
```

Check that the category distribution makes sense for your topic:
- Background categories (A/B/C): typically 70–80% of papers
- Core categories (D/E): typically 15–25% of papers
- Unrelated (F): typically <5%

### Phase 4: Full Run

```bash
python3 analyze.py
```

Crash recovery: already-processed papers are automatically skipped. Just re-run after interruption.

Monitor progress in another terminal:
```bash
watch -n 30 'ls ~/Zotero/storage/*/analysis.json | wc -l'
```

### Phase 5: Aggregate Statistics

```bash
python3 summarize.py
```

Outputs a detailed report and saves `summary.json` for use in Step 4.

## Troubleshooting

**A paper's output is clearly wrong:**
```bash
rm ~/Zotero/storage/FOLDER_NAME/analysis.json
python3 analyze.py --folder FOLDER_NAME
```

**Many scanned PDFs (text extraction fails):**
The script records `{"error": "Extracted text too short — likely a scanned PDF"}`.
Options: ignore (if few), run OCR first, or manually write `analysis.json`.

**Lots of 429 rate-limit errors:**
Increase `RATE_LIMIT_DELAY` to 1.0 or 2.0 seconds.

**Estimating cost mid-run:**
Run `python3 summarize.py` — the `_meta.input_tokens` field in each `analysis.json` lets you calculate actual cost.

## Output

Each successfully processed folder gets an `analysis.json` (1–3 KB).
Failed papers get a JSON with an `error` field.

After `summarize.py`:
- Console report: category distribution, top methods, year trends
- `summary.json`: machine-readable aggregate for Step 4
