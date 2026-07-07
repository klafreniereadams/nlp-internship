import json
import re

# code scaffolding provided by IDX Exchange
# injection-safe SQL practices following the guidelines at 
# https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

class QueryParser:
    def __init__(self, amenities_path="scripts/SQL_Queries/canonical_amenities.json"):
        with open(amenities_path) as f:
            self.amenities = json.load(f)

        self.amenity_lookup = {}
        for canonical, variants in self.amenities.items():
            for phrase in variants:
                self.amenity_lookup[phrase.lower()] = canonical

        # Build a single combined regex for all amenity phrases
        escaped = [re.escape(p) for p in self.amenity_lookup.keys()]
        escaped.sort(key=len, reverse=True)
        self.amenity_regex = re.compile(r'\b(?:' + "|".join(escaped) + r')\b', re.I)
    
    def _parse_number(self, num, suffix):
        n = int(num)
        if suffix.lower() == "k":
            return n * 1_000
        if suffix.lower() == "m":
            return n * 1_000_000
        return n

    # ---------------------------------------------
    # Amenity parsing logic setup
    # ---------------------------------------------
    def _parse_amenity_logic(self, query):
        q = query.lower()

        # Normalize "but no" → "and no"
        q = re.sub(r'\bbut no\b', 'and no', q)

        # Split on AND/OR while keeping operators
        raw_parts = re.split(r'\b(and|or)\b', q)
        parts = [p.strip() for p in raw_parts if p.strip()]

        clauses = []
        current_group = {"op": "and", "items": []}

        def flush_group():
            if current_group["items"]:
                clauses.append(current_group.copy())
                current_group["items"] = []

        pending_OR = False

        for token in parts:
            if token in ("and", "or"):
                has_negation = any("not" in item for item in current_group["items"])
                
                if token == "or":
                    if has_negation:
                    # Makes negation bind more tightly than OR. defines groups correctly before flushing.
                    # allows for "house with no hoa or pool" --> 'no hoa', 'no pool'
                    # then creates a new OR group after this one
                        pending_OR = True
                        continue
                    else:
                        flush_group()
                        current_group["op"] = "or"
                        continue
                
                # AND operator case
                current_group["op"] = "and"
                continue

            # Detect negation
            neg = bool(re.search(r'\b(no|not|without)\b', token))

            # Extract canonical amenities
            found = self.amenity_regex.findall(token)
            for f in found:
                canonical = self.amenity_lookup.get(f.lower())
                if canonical:
                    if neg or pending_OR:
                        # If OR-after-negation is pending, treat next amenity as negated
                        current_group["items"].append({"not": canonical})
                    else:
                        current_group["items"].append({"amenity": canonical})

            # If OR-after-negation was pending, now we can split
            if pending_OR:
                clauses.append(current_group.copy())
                current_group = {"op": "or", "items": []}
                pending_OR = False

        flush_group()
        return clauses

    def parse(self, query):
        filters = {}

        # ---------------------------------------------
        # Price parsing logic
        # ---------------------------------------------
        # "between min and max" price
        if match := re.search(
            r'between\s+\$?(\d+)([km]?)\s+and\s+\$?(\d+)([km]?)',
            query,
            re.I
        ):
            low = self._parse_number(match.group(1), match.group(2))
            high = self._parse_number(match.group(3), match.group(4))
            filters['price_range'] = (low, high)

        # "min - max" OR "min to max" price
        elif match := re.search(
            r'\$?(\d+)([km]?)\s*(?:-|to)\s*\$?(\d+)([km]?)',
            query,
            re.I
        ):
            low = self._parse_number(match.group(1), match.group(2))
            high = self._parse_number(match.group(3), match.group(4))
            filters['price_range'] = (low, high)

        # "over/above/at least/more than" price
        elif match := re.search(
            r'(?:over|above|at least|more than)\s+\$?(\d+)([km]?)',
            query,
            re.I
        ):
            filters['price_min'] = self._parse_number(match.group(1), match.group(2))

        # "under/below/at most" price
        elif match := re.search(
            r'(?:under|below|at most)\s+\$?(\d+)([km]?)',
            query,
            re.I
        ):
            filters['price_max'] = self._parse_number(match.group(1), match.group(2))

        # "around" price 
        # I am heuristically defining this as allowing 100k above or below stated price
        if match := re.search(
            r'(?:around|about|approximately|roughly)\s+\$?(\d+)([km]?)',
            query,
            re.I
        ):
            center = self._parse_number(match.group(1), match.group(2))
            low = max(0, center - 100_000)
            high = center + 100_000
            filters['price_range'] = (low, high)

            
        # Bedroom patterns
        if match := re.search(r'(\d+)\+?\s*(?:bed|br)', query, re.I):
            filters['bedrooms_min' if '+' in match.group(0) else 'bedrooms'] = int(match.group(1))

        # Bathroom patterns
        if match := re.search(r'(\d+)\+?\s*(?:bath|ba)', query, re.I):
            filters['bathrooms_min' if '+' in match.group(0) else 'bathrooms'] = int(match.group(1))


        # City patterns
        # allows for optional cardinal or ordinal direction + 1–3 word city name
        if match := re.search(
            r'\b(?:in|near|around|outside|close to)\s+'
            r'(?:(north|northeast|east|southeast|south|southwest|west|northwest)\s+)?'
            # stop city capture BEFORE price/bed/bath keywords
            r'([A-Za-z]+(?:\s+[A-Za-z]+){0,2})(?=\s*(?:under|over|between|below|above|at least|at most|more than|\d+\s*(?:bed|bath|br|ba)|$))',
            query,
            re.I
        ):
            #direction = match.group(1)
            city = match.group(2).title()

            # Base city assignment
            filters['city'] = city
            #---------------------------------------------------------------------------
            # removing for now because redundant, but can put back in if later want to keep directions
            # Normalizes direction and city name to title case
            #if direction:
                #direction = direction.title()
            #city = city.title()
    
            #filters['city'] = f"{direction} {city}".strip()
            #---------------------------------------------------------------------------

             # another option is for search logic to accept directional cities as variants of the base city
            # in order to not erroneously exlude "Fresno" results from a "North Fresno" search, for example.
            # This option may be dependent on the consistency of listing specificity.

            # Normalize directional cities to base city
            directions = {
                "North", "Northeast", "East", "Southeast",
                "South", "Southwest", "West", "Northwest"
            }
            parts = filters['city'].split()
            if parts[0] in directions and len(parts) > 1:
                filters['city'] = " ".join(parts[1:])

        # could this someday handle proximity queries from the user? Like "within 1 hour from LA" or 
        # "less than 20 miles from Sacramento"?
        # Would this be dependent on the strict/fuzzy calculation of the listing host's radius map tool?
        # Other workarounds?

        # ---------------------------------------------
        # Amenity logic (AND / OR / NOT)
        # ---------------------------------------------
        amenity_clauses = self._parse_amenity_logic(query)
        if amenity_clauses:
            filters["amenity_logic"] = amenity_clauses

        return filters
    
    # ---------------------------------------------
    # SQL query generation
    # ---------------------------------------------   
    def to_sql(self, filters):
        conditions = []
        params = []

        # Price range: ("price_min", "price_max") stored as a tuple
        if 'price_range' in filters:
            low, high = filters['price_range']
            conditions.append('L_SystemPrice BETWEEN %s AND %s')
            params.extend([low, high])

        # Price minimum
        if 'price_min' in filters:
            conditions.append('L_SystemPrice >= %s')
            params.append(filters['price_min'])

        # Price maximum
        if 'price_max' in filters:
            conditions.append('L_SystemPrice <= %s')
            params.append(filters['price_max'])

        # Bedrooms exact
        if 'bedrooms' in filters:
            b = filters['bedrooms']
            conditions.append(
                "("
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR"
                "L_Remarks ILIKE %s OR"
                "L_Remarks ILIKE %s"
                ")"
            )
            params.extend([
                f"%{b} bed%",
                f"%{b} beds%",
                f"%{b}br%",
                f"%{b} br%",
                f"%{b}-bed%",
                f"%{b} bdr%",
                f"%{b} bedrooms"
            ])
        # Bedrooms minimum
        if 'bedrooms_min' in filters:
            b = filters['bedrooms_min']
            conditions.append(
                "("
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s"
                ")"
            )
            params.extend([
                f"%{b} bed%",
                f"%{b} beds%",
                f"%{b}br%",
                f"%{b} br%",
                f"%{b}-bed%",
                f"%{b} bdr%",
                f"%{b} bedrooms"
            ])
    
        # Bathrooms exact
        if 'bathrooms' in filters:
            ba = filters['bathrooms']
            conditions.append(
                "("
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s "
                ")"
            )
            params.extend([
                f"%{ba} bath%",
                f"%{ba} baths%",
                f"%{ba}ba%",
                f"%{ba} ba%",
                f"%{ba}-bath%",
                f"%{ba} bth%",
                f"%{ba} bathrooms%"
            ])
        # Bathrooms minimum
        if 'bathrooms_min' in filters:
            ba = filters['bathrooms_min']
            conditions.append(
                "("
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s OR "
                "L_Remarks ILIKE %s "
                ")"
            )
            params.extend([
                f"%{ba} bath%",
                f"%{ba} baths%",
                f"%{ba}ba%",
                f"%{ba} ba%",
                f"%{ba}-bath%",
                f"%{ba} bth%",
                f"%{ba} bathrooms%"
            ])

        # City # without sensitivity to ordinal/cardinal details
        if 'city' in filters:
            conditions.append('L_City = %s')
            params.append(filters['city'])

        # ---------------------------------------------
        # Amenities (canonical_amenities.json)
        # Handles boolean operator logic
        # ---------------------------------------------
        if 'amenity_logic' in filters:
            groups = filters['amenity_logic']
            group_sql_fragments = []

            for group in groups:
                op = group["op"]  # "and" or "or"
                items = group["items"]

                item_sql = []

                for item in items:
                    # Positive amenity
                    if "amenity" in item:
                        canonical = item["amenity"]
                        variants = self.amenities.get(canonical, [])

                        ors = []
                        for v in variants:
                            ors.append("L_Remarks ILIKE %s")
                            params.append(f"%{v}%")

                        item_sql.append("(" + " OR ".join(ors) + ")")

                    # Negated amenity
                    elif "not" in item:
                        canonical = item["not"]
                        variants = self.amenities.get(canonical, [])

                        ands = []
                        for v in variants:
                            ands.append("L_Remarks NOT ILIKE %s")
                            params.append(f"%{v}%")

                        item_sql.append("(" + " AND ".join(ands) + ")")

                # Join items inside the group
                if op == "and":
                    group_sql_fragments.append("(" + " AND ".join(item_sql) + ")")
                else:  # op == "or"
                    group_sql_fragments.append("(" + " OR ".join(item_sql) + ")")

            # Now join all groups together with AND (top-level)
            # Example: (A AND B) AND (C OR D)
            if group_sql_fragments:
                conditions.append("(" + " AND ".join(group_sql_fragments) + ")")


        where_clause = ' AND '.join(conditions)
        return f"SELECT * FROM rets_property WHERE {where_clause}", params
    
# ------------------------------------------------------------------------
# Validation before generating SQL
# ------------------------------------------------------------------------

class SchemaValidator:
    def __init__(self, db_conn):
        self.db_conn = db_conn

        # this caches the cities after loading the first time
        self.valid_cities = self._load_valid_cities()

        # later, can uncomment this out to refresh the cache (i.e. if city list changes)
        # def refresh(self):
        #     self.valid_cities = self._load_valid_cities()

    def _load_valid_cities(self):
        if not self.db_conn:
            return set()

        with self.db_conn.cursor() as cur:
            cur.execute("SELECT DISTINCT L_City FROM rets_property;")
            rows = cur.fetchall()

        return {row[0] for row in rows if row[0]}

    def validate_query(self, filters):
        errors = []
        
        # Check city exists in database
        # list of cities pulled from whatever cities are present in the rets_property L_City column
        if 'city' in filters:
            if filters['city'] not in self.valid_cities:
                errors.append(f"City '{filters['city']}' not found in database")
        
        # Check price range
        if 'price_max' in filters:
            if filters['price_max'] < 100000 or filters['price_max'] > 1000000:
                errors.append(f"Price {filters['price_max']} outside typical range")

        # Check bedroom count
        if 'bedrooms' in filters:
            if filters['bedrooms'] < 1 or filters['bedrooms'] > 10:
                errors.append(f"Bedroom count of {filters['bedrooms']} seems invalid")
    
        # Check minimum bedroom count
        if 'bedrooms_min' in filters:
            if filters['bedrooms_min'] < 1 or filters['bedrooms_min'] > 10:
                errors.append(f"Minimum bedroom number of {filters['bedrooms_min']} seems invalid")
    
        # Check bathroom count
        if 'bathrooms' in filters:
            if filters['bathrooms'] < 1 or filters['bathrooms'] > 10:
                errors.append(f"Bathroom count of {filters['bathrooms']} seems invalid")
    
        # Check minimum bathroom count
        if 'bathrooms_min' in filters:
            if filters['bathrooms_min'] < 1 or filters['bathrooms_min'] > 10:
                errors.append(f"Minimum bathroom number of {filters['bathrooms_min']} seems invalid")
            
        return len(errors) == 0, errors