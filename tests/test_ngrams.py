import pandas as pd

def test_unigrams(cleaner, sample_series):
    result = cleaner.extract_top_ngrams(sample_series)
    assert "unigrams" in result

def test_bigrams(cleaner, sample_series):
    result = cleaner.extract_top_ngrams(sample_series)
    assert "bigrams" in result

def test_trigrams(cleaner, sample_series):
    result = cleaner.extract_top_ngrams(sample_series)
    assert "trigrams" in result

def test_ngrams_ignore_stopwords(cleaner):
    series = pd.Series(["the the the kitchen kitchen"])
    result = cleaner.extract_top_ngrams(series)
    assert "the" not in result["unigrams"]

def test_ngrams_alpha_only(cleaner):
    series = pd.Series(["kitchen 123 !!!"])
    result = cleaner.extract_top_ngrams(series)
    assert "kitchen" in result["unigrams"]
    assert "123" not in result["unigrams"]

def test_ngrams_no_punctuation_spanning(cleaner):
    series = pd.Series(["kitchen. large yard"])
    result = cleaner.extract_top_ngrams(series)
    assert "kitchen large" not in result["bigrams"]
