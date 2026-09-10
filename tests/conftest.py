# test suite was Copilot generated because I was in a hurry
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
    
#print("PYTEST sys.path:", sys.path)

import pytest
from scripts.Data_Preparation.text_cleaning import TextCleaner
import pandas as pd

@pytest.fixture
def cleaner():
    return TextCleaner()

@pytest.fixture
def sample_series():
    return pd.Series([
        "Beautiful 2,000 sqft home w/ updated kitchen",
        "Priced at 450k, 3br 2ba",
        "1,250 sq.ft. condo w/o garage",
        None,
        "Mbr suite with 1.2m price tag"
    ])
