# Step 1: Deduplicating Your Zotero Library

## Zotero Storage Structure

Zotero stores each paper's PDF in a separate subfolder:

```
~/Zotero/storage/
├── AAAAAAAA/
│   └── Smith2024_paper.pdf
├── BBBBBBBB/
│   └── Smith2024_paper.pdf   ← Duplicate!
├── CCCCCCCC/
│   └── Zhang2023_other.pdf
└── ...
```

Each folder is named with an 8-character random ID linked to Zotero's internal database.

## Why Duplicates Happen

1. Importing from multiple sources (Google Scholar + Web of Science + advisor recommendations)
2. Both preprint and published version imported
3. Different editions of the same book

## Method 1: Zotero Built-in Dedup (Recommended — Safest)

1. Open Zotero desktop
2. Find **Duplicate Items** in the left panel
3. Select all → right-click → **Merge Items**
4. Zotero keeps the entry with more complete metadata and merges attachments

**Always use this method when possible.** Manually deleting storage folders breaks the Zotero database.

## Method 2: MD5 Hash Detection (for verification)

```python
#!/usr/bin/env python3
"""
Detect duplicate PDFs in Zotero storage by file content hash.
Read-only — does not modify any files.
"""
import os
import hashlib
from pathlib import Path
from collections import defaultdict

STORAGE = Path.home() / "Zotero/storage"

def md5_of_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates():
    hashes = defaultdict(list)

    for folder in sorted(STORAGE.iterdir()):
        if not folder.is_dir():
            continue
        pdfs = list(folder.glob("*.pdf"))
        if not pdfs:
            continue
        pdf = pdfs[0]
        md5 = md5_of_file(pdf)
        hashes[md5].append({
            "folder": folder.name,
            "path": str(pdf),
            "filename": pdf.name,
            "size": pdf.stat().st_size,
        })

    duplicates = {h: items for h, items in hashes.items() if len(items) > 1}

    print(f"Scanned {sum(len(v) for v in hashes.values())} PDFs")
    print(f"Found {len(duplicates)} duplicate groups\n")

    for md5, items in sorted(duplicates.items()):
        print(f"Duplicate group ({len(items)} files):")
        for item in items:
            print(f"  [{item['folder']}] {item['filename']} ({item['size']//1024} KB)")
        print()

    # Suggestion: keep first, delete rest (do this in Zotero, not manually)
    to_merge = []
    for md5, items in duplicates.items():
        to_merge.append((items[0]["folder"], [i["folder"] for i in items[1:]]))

    print(f"\nSuggested merges (keep → duplicates to merge):")
    for keep, merge in to_merge:
        print(f"  Keep [{keep}], merge: {merge}")

    return to_merge

if __name__ == "__main__":
    find_duplicates()
```

**Run:**
```bash
python3 dedup_check.py
```

## Method 3: Title Similarity Detection

For cases where preprint and published version have slightly different PDFs (different hash), use title fuzzy matching after `analyze.py` has run:

```python
#!/usr/bin/env python3
"""
Detect near-duplicate papers by title similarity.
Requires analysis.json files to already exist (run analyze.py first).
"""
import json
import re
from pathlib import Path

STORAGE = Path.home() / "Zotero/storage"

def normalize_title(t):
    t = t.lower()
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def find_title_duplicates():
    papers = {}
    for folder in sorted(STORAGE.iterdir()):
        fp = folder / "analysis.json"
        if not fp.exists():
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            title = data.get("title", "")
            if title:
                norm = normalize_title(title)
                if norm in papers:
                    print(f"Possible duplicate:")
                    print(f"  [{papers[norm]}] {title}")
                    print(f"  [{folder.name}] {title}")
                    print()
                else:
                    papers[norm] = folder.name
        except Exception:
            pass

if __name__ == "__main__":
    find_title_duplicates()
```

## Handling Remaining Duplicates

If some duplicates slip through to the writing stage, document them in `TASK_FOR_WRITER.md`:

```
Duplicate pairs (cite only the first in each pair):
- AAAAAAAA = BBBBBBBB  (same paper, two import sources)
- CCCCCCCC = DDDDDDDD  (preprint vs. published version)
```

The writing LLM will then consistently cite the canonical version.
