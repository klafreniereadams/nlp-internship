import pandas as pd
#from text_cleaner.cleaner import TextCleaner #incorrect path
from scripts.Data_Preparation.text_cleaning import TextCleaner

df = pd.read_csv("data/processed/listing_remarks.csv")

def test_price_normalization():
    cleaner = TextCleaner()
    assert cleaner.normalize_prices("priced at 450k") == "priced at 450000"
    assert cleaner.normalize_prices("$1.2m home") == "$1200000 home"

def test_profile_keys():
    cleaner = TextCleaner()
    profile = cleaner.profile_column(df, "remarks")
    assert "null_rate" in profile
    assert "avg_length" in profile
    assert "common_terms" in profile
    assert "common_abbreviations" in profile
