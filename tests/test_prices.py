def test_price_k(cleaner):
    assert cleaner.normalize_prices("450k") == "450000"

def test_price_m(cleaner):
    assert cleaner.normalize_prices("1.2m") == "1200000"

def test_price_with_text(cleaner):
    assert "450000" in cleaner.normalize_prices("priced at 450k")

def test_price_decimal_k(cleaner):
    assert cleaner.normalize_prices("1.5k") == "1500"

def test_price_decimal_m(cleaner):
    assert cleaner.normalize_prices("2.75m") == "2750000"

def test_price_case_insensitive(cleaner):
    assert cleaner.normalize_prices("450K") == "450000"

def test_price_no_match(cleaner):
    assert cleaner.normalize_prices("no price here") == "no price here"
