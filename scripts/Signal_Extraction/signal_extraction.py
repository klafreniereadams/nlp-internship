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
        found = set()

        for canonical, patterns in self._amenity_patterns.items():
            for p in patterns:
                # matches only full taxonomy phrases to avoid duplication or substring mapping mistakes
                if p in remarks_norm:
                    found.append(canonical)
                    break

        return sorted(found)

    # ---------------------------------------------------------------------
    # Condition extraction
    # there is some overlap with canonical_amenities. Fleshed out with copilot
    # ---------------------------------------------------------------------
    def _extract_condition(self, remarks_norm):
        # Example starter patterns
        condition_map = {
            "updated": [
                "updated",
                "recently updated",
                "remodeled",
                "recently remodeled",
                "renovated",
                "recently renovated",
                "modernized",
                "upgraded",
                "recent upgrades",
                "newly updated",
                "newly renovated",
                "freshly updated",
                "freshly renovated",
                "updated kitchen",
                "updated bathrooms",
                "updated bath",
                "updated flooring",
                "updated appliances",
                "new paint",
                "fresh paint",
                "freshly painted",
                "newly painted"
            ],
            "new_construction": [
                "new construction",
                "brand new",
                "newly built",
                "just built",
                "construction completed",
                "never lived in",
                "new build"
            ],
            "recent_repairs": [
                "new roof",
                "roof replaced",
                "hvac replaced",
                "new hvac",
                "new furnace",
                "new water heater",
                "water heater replaced",
                "new plumbing",
                "plumbing updated",
                "electrical updated",
                "new electrical",
                "foundation repaired"
            ],
            "move_in_ready": [
                "move in ready",
                "move-in ready",
                "turnkey",
                "turn-key",
                "ready to move in",
                "ready for move in",
                "well maintained",
                "well-maintained",
                "meticulously maintained",
                "immaculately maintained"
            ]
        }

        found = set()
        for canonical, patterns in condition_map.items():
            for p in patterns:
                if p in remarks_norm:
                    found.append(canonical)
                    break
        return sorted(found)

    # ---------------------------------------------------------------------
    # Financing extraction
    # ---------------------------------------------------------------------
    def _extract_financing(self, remarks_norm):
        # Financing patterns for more precise extraction later.
        # Copilot generated since I'm unfamiliar with financing
        financing_map = {
            "seller_financing": [
                "seller financing",
                "owner financing",
                "owner will carry",
                "seller will carry",
                "seller may carry",
                "owner may carry",
                "seller carry",
                "owner carry",
                "seller finance available",
                "owner finance available",
                "seller will consider financing",
                "owner will consider financing",
                "seller terms available",
                "owner terms available"
            ],
            "assumable_loan": [
                "assumable loan",
                "assume loan",
                "loan is assumable",
                "assumable mortgage",
                "mortgage is assumable",
                "assume existing loan",
                "assume existing mortgage"
            ],
            "cash_only": [
                "cash only",
                "cash sale only",
                "cash buyers only",
                "cash purchase only"
            ],
            "va_eligible": [
                "va eligible",
                "va approved",
                "va financing available",
                "va loan available"
            ],
            "fha_eligible": [
                "fha eligible",
                "fha approved",
                "fha financing available",
                "fha loan available"
            ],
            "conventional_eligible": [
                "conventional financing",
                "conventional loan",
                "conventional financing available"
            ]
        }

        found = set()
        for canonical, patterns in financing_map.items():
            for p in patterns:
                if p in remarks_norm:
                    found.append(canonical)
                    break
        return sorted(found)

    # ---------------------------------------------------------------------
    # Location extraction # some overlap with canonical amenities that mention views and nearby businesses
    # ---------------------------------------------------------------------
    def _extract_location(self, remarks_norm):
        # mappings expanded with copilot
        location_map = {
            "mountain_views": [
                "mountain views",
                "views of the mountains",
                "mountain view",
                "view of the mountains",
                "mountain vista",
                "mountain vistas",
                "scenic mountain views"
            ],
            "lake_views": [
                "lake view",
                "lake views",
                "views of the lake",
                "waterfront view",
                "lakefront",
                "on the lake",
                "near the lake"
            ],
            "near_schools": [
                "near schools",
                "close to schools",
                "walking distance to schools",
                "walk to school",
                "nearby schools",
                "close to elementary",
                "close to high school"
            ],
            "near_parks": [
                "near parks",
                "close to parks",
                "walking distance to parks",
                "walk to park",
                "nearby park",
                "adjacent to park",
                "next to park"
            ],
            "near_shopping": [
                "near shopping",
                "close to shopping",
                "near shops",
                "close to shops",
                "shopping nearby",
                "minutes from shopping",
                "near retail",
                "close to retail"
            ],
            "near_public_transport": [
                "near public transport",
                "close to public transport",
                "near transit",
                "close to transit",
                "near bus stop",
                "close to bus stop",
                "near train station",
                "close to train station"
            ],
            "golf_course": [
                "on the golf course",
                "near golf course",
                "golf course views",
                "golf course community",
                "adjacent to golf course"
            ],
            "cul_de_sac": [
                "cul de sac",
                "cul-de-sac",
                "quiet cul de sac",
                "located on a cul de sac"
            ]
        }

        found = set()
        for canonical, patterns in location_map.items():
            for p in patterns:
                if p in remarks_norm:
                    found.append(canonical)
                    break
        return sorted()