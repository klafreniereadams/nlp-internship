# process_signals.py

from pathlib import Path
import csv
import json
from signal_extraction import SignalExtractor

def load_listings():
    script_dir = Path(__file__).resolve().parent

    # project_root/data/processed/listing_remarks.csv
    csv_path = script_dir.parent.parent / "data" / "processed" / "listing_remarks.csv"

    listings = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            listings.append(row)
    return listings

def main():
    script_dir = Path(__file__).resolve().parent

    # project_root/scripts/SQL_Queries/canonical_amenities.json
    taxonomy_path = script_dir.parent / "SQL_Queries" / "canonical_amenities.json"

    extractor = SignalExtractor(taxonomy_path=taxonomy_path, entity_extractor=None)

    listings = load_listings()

    processed_dir = script_dir / "processed"
    processed_dir.mkdir(exist_ok=True)

    for listing in listings:
        signals = extractor.extract_signals(listing)

        out_path = processed_dir / f"{listing['L_ListingID']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2)

if __name__ == "__main__":
    main()