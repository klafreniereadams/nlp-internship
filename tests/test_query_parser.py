import pytest
from scripts.SQL_Queries.query_parser import QueryParser, SchemaValidator

# Fake DB connection returning a fixed set of valid CA cities
class FakeConn:
    def cursor(self):
        return self
    def execute(self, _):
        pass
    def fetchall(self):
        return [
            ("Los Angeles",), # cities chosen deterministically for isolated, safe testing
            ("San Diego",),
            ("San Jose",),
            ("Sacramento",),
            ("Fresno",),
            ("Irvine",),
            ("Oakland",),
            ("Bakersfield",),
            ("Anaheim",),
        ]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

parser = QueryParser()
validator = SchemaValidator(db_conn=FakeConn())

# 1. Price: under
def test_price_under_700k():
    f = parser.parse("3 bed in Irvine under 700k")
    assert f["price_max"] == 700000

# 2. Price: between
def test_price_between_range():
    f = parser.parse("between 400k and 900k in Fresno")
    assert f["price_range"] == (400000, 900000)

# 3. Price: over
def test_price_over_1m():
    f = parser.parse("house over 1m in Sacramento")
    assert f["price_min"] == 1_000_000

# 4. Bedrooms exact
def test_bedrooms_exact_4():
    f = parser.parse("4 bed in Oakland")
    assert f["bedrooms"] == 4

# 5. Bedrooms minimum
def test_bedrooms_min_3_plus():
    f = parser.parse("3+ bed in San Diego")
    assert f["bedrooms_min"] == 3

# 6. Bathrooms exact
def test_bathrooms_exact_2():
    f = parser.parse("2 bath in Los Angeles")
    assert f["bathrooms"] == 2

# 7. Bathrooms minimum
def test_bathrooms_min_2_plus():
    f = parser.parse("2+ bath in San Jose")
    assert f["bathrooms_min"] == 2

# 8. City validation: valid
def test_city_valid_irvine():
    f = parser.parse("3 bed in Irvine")
    valid, errors = validator.validate_query(f)
    assert valid

# 9. City validation: invalid
def test_city_invalid_atlantis():
    f = parser.parse("3 bed in Atlantis")
    valid, errors = validator.validate_query(f)
    assert not valid
    assert "not found" in errors[0].lower()

# 10. SQL injection protection: no raw concat
def test_sql_injection_protection():
    f = parser.parse("3 bed in Irvine; DROP TABLE rets_property;")
    sql, params = parser.to_sql(f)

    # SQL must not contain injected commands
    assert "DROP TABLE" not in sql.upper()

    # Params must be separate from SQL
    assert all(isinstance(p, (str, int)) for p in params)

# 11. Amenity: simple AND
def test_amenity_pool_and_garage():
    f = parser.parse("house with pool and garage")
    logic = f["amenity_logic"]
    assert logic[0]["op"] == "and"
    assert {"amenity": "pool"} in logic[0]["items"]
    assert {"amenity": "garage"} in logic[0]["items"]

# 12. Amenity: simple OR
def test_amenity_pool_or_yard():
    f = parser.parse("house with pool or yard")
    logic = f["amenity_logic"]
    assert logic[1]["op"] == "or"

# 13. Amenity: AND + OR mix
def test_amenity_pool_and_garage_or_carport():
    f = parser.parse("house with pool and garage or carport")
    logic = f["amenity_logic"]
    assert logic[0]["op"] == "and"
    assert logic[1]["op"] == "or"

# 14. Amenity: negation (NO)
def test_amenity_no_hoa():
    f = parser.parse("house with no hoa")
    logic = f["amenity_logic"]
    assert {"not": "hoa"} in logic[0]["items"]

# 15. Amenity: BUT NO → AND NO
def test_amenity_pool_but_no_hoa():
    f = parser.parse("house with pool but no hoa")
    logic = f["amenity_logic"]
    assert {"amenity": "pool"} in logic[0]["items"]
    assert {"not": "hoa"} in logic[0]["items"]

# 16. Amenity: AND NO
def test_amenity_garage_and_no_yard():
    f = parser.parse("house with garage and no yard")
    logic = f["amenity_logic"]
    assert {"amenity": "garage"} in logic[0]["items"]
    assert {"not": "yard"} in logic[0]["items"]

# 17. Price: around
def test_price_around_600k():
    f = parser.parse("around 600k in Fresno")
    low, high = f["price_range"]
    assert low == 500000
    assert high == 700000

# 18. Price: approximately
def test_price_approximately_450k():
    f = parser.parse("approximately 450k in Sacramento")
    low, high = f["price_range"]
    assert low == 350000
    assert high == 550000

# 19. City parsing with direction (normalized)
def test_city_north_fresno_normalized():
    f = parser.parse("3 bed in North Fresno under 500k")
    assert f["city"] == "Fresno"

# 20. City validation: out-of-range price
def test_price_max_out_of_range():
    f = parser.parse("3 bed in Irvine under 5m")
    valid, errors = validator.validate_query(f)
    assert not valid
    assert "outside typical range" in errors[0].lower()

# 21. Price: below
def test_price_below_300k():
    f = parser.parse("studio below 300k in Anaheim")
    assert f["price_max"] == 300000

# 22. Price: at most
def test_price_at_most_800k():
    f = parser.parse("home at most 800k in San Diego")
    assert f["price_max"] == 800000

# 23. Price: more than
def test_price_more_than_900k():
    f = parser.parse("condo more than 900k in Los Angeles")
    assert f["price_min"] == 900000

# 24. Bedrooms: multiple digit
def test_bedrooms_exact_10():
    f = parser.parse("10 bed in Fresno")
    assert f["bedrooms"] == 10

# 25. Bedrooms: invalid high count
def test_bedrooms_invalid_20():
    f = parser.parse("20 bed in Irvine")
    valid, errors = validator.validate_query(f)
    assert not valid
    assert "invalid" in errors[0].lower()

# 26. Bathrooms: multiple digit
def test_bathrooms_exact_8():
    f = parser.parse("8 bath in Sacramento")
    assert f["bathrooms"] == 8

# 27. Bathrooms: invalid high count
def test_bathrooms_invalid_15():
    f = parser.parse("15 bath in Oakland")
    valid, errors = validator.validate_query(f)
    assert not valid
    assert "invalid" in errors[0].lower()

# 28. Amenity: multiple AND chain
def test_amenity_pool_garage_yard_chain():
    f = parser.parse("house with pool and garage and yard")
    logic = f["amenity_logic"]
    assert logic[0]["op"] == "and"
    assert {"amenity": "pool"} in logic[0]["items"]
    assert {"amenity": "garage"} in logic[0]["items"]
    assert {"amenity": "yard"} in logic[0]["items"]

# 29. Amenity: OR chain
def test_amenity_pool_or_garage_or_yard():
    f = parser.parse("house with pool or garage or yard")
    logic = f["amenity_logic"]
    assert logic[1]["op"] == "or"

# 30. Amenity: mixed negation and OR
def test_amenity_no_hoa_or_pool():
    f = parser.parse("house with no hoa or pool")
    logic = f["amenity_logic"]
    # first group: negation
    assert {"not": "hoa"} in logic[0]["items"]
    # second group: OR group
    assert logic[1]["op"] == "or"
    assert {"amenity": "pool"} in logic[1]["items"]

# 31. Amenity: NOT + AND chain
def test_amenity_no_pool_and_garage():
    f = parser.parse("house with no pool and garage")
    logic = f["amenity_logic"]
    assert {"not": "pool"} in logic[0]["items"]
    assert {"amenity": "garage"} in logic[0]["items"]

# 32. Amenity: NOT + OR chain
def test_amenity_no_yard_or_pool():
    f = parser.parse("house with no yard or pool")
    logic = f["amenity_logic"]
    assert {"not": "yard"} in logic[0]["items"]
    assert logic[1]["op"] == "or"
    assert {"amenity": "pool"} in logic[1]["items"]

# 33. Amenity: triple negation
def test_amenity_no_pool_no_garage_no_yard():
    f = parser.parse("house with no pool and no garage and no yard")
    logic = f["amenity_logic"]
    items = logic[0]["items"]
    assert {"not": "pool"} in items
    assert {"not": "garage"} in items
    assert {"not": "yard"} in items

# 34. Price: hyphen range
def test_price_hyphen_range():
    f = parser.parse("450k - 650k in San Jose")
    assert f["price_range"] == (450000, 650000)

# 35. Price: to range
def test_price_to_range():
    f = parser.parse("300k to 500k in Oakland")
    assert f["price_range"] == (300000, 500000)

# 36. Price: malformed but still safe
def test_price_malformed_injection_attempt():
    f = parser.parse("under 500k; DROP TABLE users; in Irvine")
    sql, params = parser.to_sql(f)
    assert "DROP TABLE" not in sql.upper()
    assert isinstance(params[0], int)

# 37. City: near keyword
def test_city_near_keyword():
    f = parser.parse("3 bed near Fresno")
    assert f["city"] == "Fresno"

# 38. City: around keyword
def test_city_around_keyword():
    f = parser.parse("2 bath around Sacramento")
    assert f["city"] == "Sacramento"

# 39. City: close to keyword
def test_city_close_to_keyword():
    f = parser.parse("house close to San Diego under 900k")
    assert f["city"] == "San Diego"

# 40. City: outside keyword
def test_city_outside_keyword():
    f = parser.parse("condo outside Los Angeles under 700k")
    assert f["city"] == "Los Angeles"

# 41. Amenity: OR with negation
def test_amenity_pool_or_no_hoa():
    f = parser.parse("house with pool or no hoa")
    logic = f["amenity_logic"]
    assert logic[1]["op"] == "or"
    assert {"amenity": "pool"} in logic[1]["items"]
    assert {"not": "hoa"} in logic[1]["items"]

# 42. Amenity: AND + OR + NOT mix
def test_amenity_pool_and_no_yard_or_garage():
    f = parser.parse("house with pool and no yard or garage")
    logic = f["amenity_logic"]
    assert logic[0]["op"] == "and"
    assert {"amenity": "pool"} in logic[0]["items"]
    assert {"not": "yard"} in logic[0]["items"]
    assert logic[1]["op"] == "or"
    assert {"amenity": "garage"} in logic[1]["items"]

# 43. Price: million suffix
def test_price_m_suffix():
    f = parser.parse("home under 2m in Los Angeles")
    assert f["price_max"] == 2_000_000

# 44. Price: mixed suffixes
def test_price_mixed_suffixes():
    f = parser.parse("between 500k and 2m in San Diego")
    assert f["price_range"] == (500000, 2000000)

# 45. Bedrooms: br variant
def test_bedrooms_br_variant():
    f = parser.parse("3br in Irvine")
    assert f["bedrooms"] == 3

# 46. Bathrooms: ba variant
def test_bathrooms_ba_variant():
    f = parser.parse("2ba in Fresno")
    assert f["bathrooms"] == 2

# 47. SQL injection: OR 1=1 attempt
def test_sql_injection_or_true():
    f = parser.parse("3 bed in Irvine OR 1=1")
    sql, params = parser.to_sql(f)
    assert "1=1" not in sql
    assert "OR 1=1" not in sql.upper()

# 48. SQL injection: comment attempt
def test_sql_injection_comment():
    f = parser.parse("2 bath in San Jose -- drop table")
    sql, params = parser.to_sql(f)
    assert "--" not in sql
    assert "DROP TABLE" not in sql.upper()

# 49. City validation: lowercase input
def test_city_lowercase_input():
    f = parser.parse("3 bed in irvine")
    valid, errors = validator.validate_query(f)
    assert valid

# 50. City validation: mixed case input
def test_city_mixed_case_input():
    f = parser.parse("4 bed in SaN dIeGo")
    valid, errors = validator.validate_query(f)
    assert valid

