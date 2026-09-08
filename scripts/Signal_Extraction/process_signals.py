# process_signals.py

from pathlib import Path
import csv
import json
from scripts.Signal_Extraction.combined_extraction import build_combined_extractor

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

    # Uses the combined Week 3 and Week 6 extractors
    extractor = build_combined_extractor()
    listings = load_listings()
    processed_dir = script_dir.parent.parent / "data" / "processed" / "Signals"
    processed_dir.mkdir(exist_ok=True)

    total = len(listings)
    
    for idx, listing in enumerate(listings, start=1):
        signals = extractor.extract_signals(listing)

        out_path = processed_dir / f"{listing['L_ListingID']}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2)

        if idx % 100 == 0:
            print(f"Processed {idx}/{total} listings...")

    print("Signal extraction complete.")

if __name__ == "__main__":
    main()