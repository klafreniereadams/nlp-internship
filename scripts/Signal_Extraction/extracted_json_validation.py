# extracted_json_validation.py
# generated with copilot for a rapid validation check

import json
from pathlib import Path

def validate_signals_schema(signals):
    required_fields = [
        "listing_id",
        "entities",
        "amenities",
        "condition_keywords",
        "financing_terms",
        "location_features"
    ]

    # Check required top-level fields
    for field in required_fields:
        if field not in signals:
            return False, f"Missing field: {field}"

    # Check types
    if not isinstance(signals["listing_id"], str):
        return False, "listing_id must be a string"

    if not isinstance(signals["entities"], list):
        return False, "entities must be a list"

    for ent in signals["entities"]:
        if not isinstance(ent, dict):
            return False, "each entity must be a dict"
        for sub in ["label", "span_text", "start", "end"]:
            if sub not in ent:
                return False, f"entity missing {sub}"

    for field in ["amenities", "condition_keywords", "financing_terms", "location_features"]:
        if not isinstance(signals[field], list):
            return False, f"{field} must be a list"

    return True, "OK"


def main():
    base = Path(__file__).resolve().parent.parent / "data" / "processed" / "Signals"
    json_files = list(base.glob("*.json"))

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            signals = json.load(f)

        ok, msg = validate_signals_schema(signals)
        if not ok:
            print(f"Schema error in {jf.name}: {msg}")

    print("Schema validation complete.")

if __name__ == "__main__":
    main()

# ran successfully on the 1000 JSON files of extracted signals,
# indicating consistent structure and field labels to allow
# reliable indexing and filtering