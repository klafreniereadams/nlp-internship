# filtering.py
# filters listing results for later API endpoint in app

def apply_filters(results, filters):
    filtered = []

    for item in results:
        listing = item["listing"]
        keep = True

        # Price range
        if "price_range" in filters:
            low, high = filters["price_range"]
            price = listing.get("price")
            if price is None or price < low or price > high:
                keep = False

        # Price minimum
        if keep and "price_min" in filters:
            if listing.get("price") is None or listing.get("price") < filters["price_min"]:
                keep = False

        # Price maximum
        if keep and "price_max" in filters:
            if listing.get("price") is None or listing.get("price") > filters["price_max"]:
                keep = False

        # Bedrooms exact
        if keep and "bedrooms" in filters:
            if listing.get("beds") != filters["bedrooms"]:
                keep = False

        # Bedrooms minimum
        if keep and "bedrooms_min" in filters:
            if listing.get("beds") is None or listing.get("beds") < filters["bedrooms_min"]:
                keep = False

        # Bathrooms exact
        if keep and "bathrooms" in filters:
            if listing.get("baths") != filters["bathrooms"]:
                keep = False

        # Bathrooms minimum
        if keep and "bathrooms_min" in filters:
            if listing.get("baths") is None or listing.get("baths") < filters["bathrooms_min"]:
                keep = False

        # City
        if keep and "city" in filters:
            if listing.get("L_City") != filters["city"]:
                keep = False

        # Amenity logic (canonical_amenities.json)
        if keep and "amenity_logic" in filters:
            remarks = listing.get("remarks", "").lower()
            for group in filters["amenity_logic"]:
                op = group["op"]
                items = group["items"]

                if op == "and":
                    for item_logic in items:
                        if "amenity" in item_logic:
                            if item_logic["amenity"].lower() not in remarks:
                                keep = False
                                break
                        elif "not" in item_logic:
                            if item_logic["not"].lower() in remarks:
                                keep = False
                                break
                else:  # OR group
                    or_match = False
                    for item_logic in items:
                        if "amenity" in item_logic:
                            if item_logic["amenity"].lower() in remarks:
                                or_match = True
                        elif "not" in item_logic:
                            if item_logic["not"].lower() not in remarks:
                                or_match = True
                    if not or_match:
                        keep = False

        if keep:
            filtered.append(item)

    return filtered
