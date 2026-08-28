# signal_extraction.py
from pathlib import Path
import json
import re

# uses amenity taxonomy at scripts/SQL_Queries/canonical_amenities.json
# combines output with that of Week 3's NER pipeline

# Signal extraction transforms natural text into standardized signals that can be parsed, ranked, stored, etc
class SignalExtractor:
    def __init__(self, taxonomy_path=None, entity_extractor=None):
        self.script_dir = Path(__file__).resolve().parent

        # If caller provides a taxonomy path, use it.
        # Otherwise fall back to: project_root/scripts/SQL_Queries/canonical_amenities.json
        if taxonomy_path is None:
            self.taxonomy_path = (
                self.script_dir.parent / "SQL_Queries" / "canonical_amenities.json"
            )
        else:
            self.taxonomy_path = Path(taxonomy_path)

        # Load taxonomy JSON
        with open(self.taxonomy_path, "r") as f:
            self.taxonomy = json.load(f)

        self.extractor = entity_extractor

        # Precompile lowercase patterns for speed
        self._amenity_patterns = {
            canonical: [p.lower() for p in patterns]
            for canonical, patterns in self.taxonomy.items()
        }

    def extract_signals(self, listing_record):
        remarks = listing_record.get("L_Remarks", "") or ""
        remarks_norm = remarks.lower()

        entities = self.extractor.extract_all(remarks)
        amenities = self._match_amenities(remarks_norm)

        return {
            "listing_id": listing_record["L_ListingID"],
            "entities": entities,
            "amenities": amenities,
            "condition_keywords": self._extract_condition(remarks_norm),
            "financing_terms": self._extract_financing(remarks_norm),
            "location_features": self._extract_location(remarks_norm)
        }

    # ---------------------------------------------------------------------
    # Amenity extraction using taxonomy JSON
    # ---------------------------------------------------------------------
    def _match_amenities(self, remarks_norm):
        found = []

        for canonical, patterns in self._amenity_patterns.items():
            for p in patterns:
                # simple substring match (fast + effective)
                if p in remarks_norm:
                    found.append(canonical)
                    break

        return found

    # ---------------------------------------------------------------------
    # Condition extraction (placeholder — we will fill this next)
    # ---------------------------------------------------------------------
    def _extract_condition(self, remarks_norm):
        # Example starter patterns
        condition_map = {
            "updated": ["updated", "remodeled", "renovated"],
            "new_construction": ["new construction", "brand new"]
        }

        found = []
        for canonical, patterns in condition_map.items():
            for p in patterns:
                if p in remarks_norm:
                    found.append(canonical)
                    break
        return found

    # ---------------------------------------------------------------------
    # Financing extraction (placeholder)
    # ---------------------------------------------------------------------
    def _extract_financing(self, remarks_norm):
        financing_map = {
            "seller_financing": ["seller financing", "owner will carry"],
            "assumable_loan": ["assumable loan", "assume loan"]
        }

        found = []
        for canonical, patterns in financing_map.items():
            for p in patterns:
                if p in remarks_norm:
                    found.append(canonical)
                    break
        return found

    # ---------------------------------------------------------------------
    # Location extraction (placeholder)
    # ---------------------------------------------------------------------
    def _extract_location(self, remarks_norm):
        location_map = {
            "mountain_views": ["mountain views", "views of the mountains"],
            "near_schools": ["near schools", "close to schools"]
        }

        found = []
        for canonical, patterns in location_map.items():
            for p in patterns:
                if p in remarks_norm:
                    found.append(canonical)
                    break
        return found