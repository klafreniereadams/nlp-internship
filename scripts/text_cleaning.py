from pydoc import text
import re
import pandas as pd
import unicodedata
from collections import Counter
import nltk
from nltk.corpus import stopwords

df = pd.read_csv("data/processed/listing_remarks.csv")

class TextCleaner:
    def __init__(self):
        self.abbrev_map = {
            'br': 'bedroom', 'ba': 'bathroom', 'sqft': 'square feet',
            'w/': 'with', 'w/o': 'without', 'mbr': 'master bedroom'
        }

    def clean_text(self, text):
        text = self.normalize_unicode(text)
        text = self.normalize_prices(text)
        text = self.normalize_measurements(text)
        text = self.expand_abbreviations(text)
        text = self.inclusive_language_conversion(text)
        return text.strip()
    
    # identifies and counts common abbreviations in listing remarks CONFORMING TO ABBREV LIST
    def detect_my_abbreviations(self, series, min_count=2):
        counts = {}
        for abbr in self.abbrev_map.keys():
            pattern = re.escape(abbr)
            count = series.str.contains(pattern, case=False, regex=True).sum() # will return a numpy integer e.g. "np.int64(35)"
            count = int(count) # now returns a more readable, plain integer e.g. 35
            if count >= min_count:          
                counts[abbr] = count
        return counts
    
    #def detect_all_abbreviations(self, series, max_len=5, top_n=20, min_count=5):
    # Extracts tokens that look like abbreviations: 1-max_len letters, can have a slash within the token
    # can have trailing letters
        pattern = r'\b[A-Za-z]{1,' + str(max_len) + r'}(?:/[A-Za-z]+)?\b'

        tokens = (
            series
            .str.findall(pattern, flags=re.I)
            .explode()
            .str.lower()
        )

        # Also ignore common stopwords
        stop_words = set(stopwords.words('english'))
        filtered = tokens[tokens.notna() & (~tokens.isin(stop_words)) & (~tokens.isin(["with", "this", "your", "an", "or"]))]

        # Counts the frequency of each token
        counts = filtered.value_counts()

        # Must occur more than the minimum count to be listed
        counts = counts[counts >= min_count]

        # Returns top N items as a dict
        return counts.head(top_n).to_dict()


    #i.e. br → bedroom, 2,000 sqft → 2000 square feet
    def expand_abbreviations(self, text):
        for abbr, full in self.abbrev_map.items():
            if abbr.isalpha():
                # handles br, ba, sqft, mbr
                pattern = r'\b' + re.escape(abbr) + r'\b'
            else:
                # handles w/, w/o
                pattern = re.escape(abbr)
            text = re.sub(pattern, full, text, flags=re.I)
        return text
    

    def extract_top_ngrams(self, series, top_n=20):
        # Joins all the text into one string for processing
        text = " ".join(series.dropna().astype(str).str.lower())

        # Tokenizes
        tokens = nltk.word_tokenize(text)

        # Filter out common stopwords e.g. 'the', 'and', 'a'
        stop_words = set(stopwords.words('english'))
        alpha_tokens = [t for t in tokens if t.isalpha() and t not in stop_words]


        # Builds n‑grams up to 3
        unigrams = alpha_tokens
        bigrams = list(nltk.ngrams(alpha_tokens, 2))
        trigrams = list(nltk.ngrams(alpha_tokens, 3))

        # Counts frequencies
        uni_counts = Counter(unigrams).most_common(top_n)
        bi_counts = Counter(bigrams).most_common(top_n)
        tri_counts = Counter(trigrams).most_common(top_n)

        # Converts tuples to readable strings
        return {
            "unigrams": {w: c for w, c in uni_counts},
            "bigrams": {" ".join(w): c for w, c in bi_counts},
            "trigrams": {" ".join(w): c for w, c in tri_counts},
        }


    # i.e. 2,000 sqft → 2000 square feet
    def normalize_measurements(self, text):
        if not isinstance(text, str):
            return text
        
        # Removes commas from within numbers
        text = re.sub(r'(\d),(?=\d{3}\b)', r'\1', text)

        # extra robust handling of "square feet" variations
        sqft_pattern = r'(\d+)\s*(sq\s*\.?\s*ft|sqft|sq\.?ft\.?)'
        text = re.sub(
            sqft_pattern,
            lambda m: f"{m.group(1)} {self.abbrev_map['sqft']}",
            text,
            flags=re.I
        )
        return text
        
    def normalize_prices(self, text):
        # 450k → 450000 for integers
        text = re.sub(r'(\d+)k', lambda m: str(int(m.group(1))*1000), text, flags=re.I)
        # 4.5k → 4500 for decimals
        text = re.sub(r'(\d+\.?\d*)k',lambda m: str(int(float(m.group(1)) * 1000)), text, flags=re.I)
        # 1.2m → 1200000
        text = re.sub(r'(\d+\.?\d*)m', lambda m: str(int(float(m.group(1))*1000000)), text, flags=re.I)
        return text
    
    def normalize_unicode(self, text):
        if not isinstance(text, str):
            return text

        # Normalizes composed/decomposed characters
        text = unicodedata.normalize("NFKC", text)

        # Replaces any curly quotes with straight quotes
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")

        # Replaces any em dashes with en dashes
        text = text.replace("—", "-").replace("–", "-")

        # Removes non‑breaking spaces and nonstandard whitespace
        text = text.replace("\u00A0", " ")   # non-breaking spaces
        text = re.sub(r"\s+", " ", text)     # multiple spaces

        # Strips leading/trailing whitespace
        return text.strip()

    # more and more design and real estate professionals are swapping out terms with negative connotations/origins 
    # for more neutral terms. "Master" bedroom/bathroom → primary bedroom/bathroom
    def inclusive_language_conversion(self, text):
        text = re.sub(r'(\d+)k', lambda m: str(int(m.group(1))*1000), text, flags=re.I)
        return text


    # returns some dictionary statistics to understand L_remarks before using
    def profile_column(self, df, column_name):
        return {
            'null_rate': df[column_name].isnull().mean(),
            'avg_length': df[column_name].str.len().mean(),
            'common_terms': self.extract_top_ngrams(df[column_name], top_n=20),
            'price_mentions': df[column_name].str.contains(r'\$\d').sum(),
            'has_html': df[column_name].str.contains('<').sum(),
            'common_abbreviations': self.detect_my_abbreviations(df[column_name])
        }


# Use to guide cleaning strategy:
cleaner = TextCleaner()
profile = cleaner.profile_column(df, 'remarks')
print()
print(f"HTML tags found in {profile['has_html']} listings")
print()
print(f"Common abbreviations: {profile['common_abbreviations']}")
print()
print(f"Top unigrams: {profile['common_terms']['unigrams']}")
print()
print(f"Top bigrams: {profile['common_terms']['bigrams']}")
print()
print(f"Top trigrams: {profile['common_terms']['trigrams']}")

print("normalize_prices loaded from:", __file__)

# Testing cleaner functionality
def test_price_normalization():
    cleaner = TextCleaner()
    assert '450000' in cleaner.normalize_prices('priced at 450k')
    assert '1200000' in cleaner.normalize_prices('$1.2m home')

def test_profiling():
    profile = cleaner.profile_column(df, 'remarks')
    assert 'null_rate' in profile
    assert 'avg_length' in profile