def test_sqft_basic(cleaner):
    assert cleaner.normalize_measurements("2000 sqft") == "2000 square feet"

def test_sq_ft(cleaner):
    assert cleaner.normalize_measurements("1500 sq ft") == "1500 square feet"

def test_sqft_with_commas(cleaner):
    assert cleaner.normalize_measurements("2,000 sqft") == "2000 square feet"

def test_sqft_dot(cleaner):
    assert cleaner.normalize_measurements("1,250 sq.ft.") == "1250 square feet"

def test_sqft_no_space(cleaner):
    assert cleaner.normalize_measurements("1200sqft") == "1200 square feet"

def test_sqft_case_insensitive(cleaner):
    assert cleaner.normalize_measurements("900 SQ FT") == "900 square feet"

def test_measurements_non_string(cleaner):
    assert cleaner.normalize_measurements(None) is None
