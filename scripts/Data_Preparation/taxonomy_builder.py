import string
import nltk
import json
import pandas as pd
import mysql.connector
from collections import Counter
from nltk.util import ngrams
from nltk.corpus import stopwords

query = """
SELECT L_remarks as remarks
FROM rets_property
WHERE L_remarks IS NOT NULL;
"""
conn = mysql.connector.connect(
host='localhost', user='root', password='root', database='real_estate')

df = pd.read_sql(query, conn)
df = df[df['remarks'].str.len() > 50].copy()
df.to_csv('data/processed/listing_sample.csv', index=False)
conn.close()


# Extract bigrams from remarks with some quick cleaning
all_text = ' '.join(df['remarks'].dropna().str.lower().str.replace(r"\s+", " ", regex=True))
#stops = set(stopwords.words("english"))
stops = {"the", "and", "an", "a", "or", "but", "is", "are", "was", "were", "be", "been", 
         "on", "at", "it", "its", "it's", "as", "if", "this", "that", "these", "those", "n't", "'ll", "you", "' ll", "'s", "do", "with", "to", "' re", "ll",
         "home", "house", "property", "has", "have"}

tokens = nltk.word_tokenize(all_text)
tokens = [
    t for t in tokens
    if t not in stops and t not in string.punctuation
    ]
bigrams = list(ngrams(tokens, 2))
freq = Counter(bigrams)

# Print top 200 bigrams
for bigram, count in freq.most_common(200):
    print(f"{' '.join(bigram)}: {count}")

# Write top 200 bigramsto taxonomy.json as taxonomy seed
top_bigrams = [
    {"id": i+1, "term": " ".join(bigram)}
    for i, (bigram, count) in enumerate(freq.most_common(200))
]

taxonomy = {"terms": top_bigrams}

with open("data/processed/taxonomy.json", "w") as f:
    json.dump(taxonomy, f, indent=2)