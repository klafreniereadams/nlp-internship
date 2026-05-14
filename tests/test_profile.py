import pandas as pd

def test_profile_keys(cleaner, sample_series):
    profile = cleaner.profile_column(pd.DataFrame({"remarks": sample_series}), "remarks")
    assert "null_rate" in profile
    assert "avg_length" in profile
    assert "common_terms" in profile
    assert "common_abbreviations" in profile

def test_profile_null_rate(cleaner):
    series = pd.Series(["a", None, None])
    profile = cleaner.profile_column(pd.DataFrame({"remarks": series}), "remarks")
    assert profile["null_rate"] == 2/3

def test_profile_avg_length(cleaner):
    series = pd.Series(["abc", "abcd"])
    profile = cleaner.profile_column(pd.DataFrame({"remarks": series}), "remarks")
    assert profile["avg_length"] == 3.5

def test_profile_html_detection(cleaner):
    series = pd.Series(["<p>hello</p>", "no html"])
    profile = cleaner.profile_column(pd.DataFrame({"remarks": series}), "remarks")
    assert profile["has_html"] == 1

def test_profile_price_mentions(cleaner):
    series = pd.Series(["$500k home", "no price"])
    profile = cleaner.profile_column(pd.DataFrame({"remarks": series}), "remarks")
    assert profile["price_mentions"] == 1

def test_profile_abbrev_counts(cleaner):
    series = pd.Series(["3 br", "2 ba", "no abbrev"])
    profile = cleaner.profile_column(pd.DataFrame({"remarks": series}), "remarks")
    assert "br" in profile["common_abbreviations"]

def test_profile_ngrams_structure(cleaner, sample_series):
    profile = cleaner.profile_column(pd.DataFrame({"remarks": sample_series}), "remarks")
    assert isinstance(profile["common_terms"], dict)

def test_profile_handles_empty(cleaner):
    df = pd.DataFrame({"remarks": []})
    profile = cleaner.profile_column(df, "remarks")
    assert "null_rate" in profile
