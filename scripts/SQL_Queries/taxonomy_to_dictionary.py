# produced with Copilot to quickly convert my taxonomy.json to a 
# more robust amenity dictionary that associates multiple variations 
# of the same amenity

# outputs --> canonical_amenities.json

import json
import re
from pathlib import Path

# -----------------------------
# 1. Canonical key generator
# -----------------------------
def canonical_key(term: str) -> str:
    term = term.lower()
    term = re.sub(r"[^a-z0-9]+", "_", term)
    term = re.sub(r"_+", "_", term)
    return term.strip("_")


# -----------------------------
# 2. Basic synonym expansion
# -----------------------------
def expand_synonyms(term: str) -> list[str]:
    t = term.lower()
    variants = {t}

    # hyphen → space
    variants.add(t.replace("-", " "))

    # remove hyphens entirely
    variants.add(t.replace("-", ""))

    # pluralize last word (simple heuristic)
    parts = t.split()
    if len(parts) > 1:
        variants.add(" ".join(parts[:-1] + [parts[-1] + "s"]))

    return sorted(variants)


# -----------------------------
# 3. Build canonical dictionary
# -----------------------------
def build_canonical_dict(input_path: str, output_path: str):
    raw = json.loads(Path(input_path).read_text())["terms"]

    canonical = {}

    for item in raw:
        term = item["term"]
        key = canonical_key(term)
        synonyms = expand_synonyms(term)
        canonical[key] = synonyms

    Path(output_path).write_text(
        json.dumps(canonical, indent=2, ensure_ascii=False)
    )

    print(f"Canonical amenity dictionary written to {output_path}")


# -----------------------------
# 4. Run it
# -----------------------------
if __name__ == "__main__":
    build_canonical_dict(
        input_path="data/processed/taxonomy.json",
        output_path="scripts/SQL_Queries/canonical_amenities.json"
    )
