from rank_bm25 import BM25Okapi
import pandas as pd
import numpy as np

class BM25Searcher:
    def __init__(self, remarks_path="data/processed/listing_remarks.csv"):
        df = pd.read_csv(remarks_path)
        self.listings = df["remarks"].fillna("").tolist()

        # Tokenize remarks for BM25
        self.tokenized = [remark.lower().split() for remark in self.listings]
        self.bm25 = BM25Okapi(self.tokenized)

    def search(self, query, top_k=10):
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)

        # Get top_k indices sorted by score descending
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = [(self.listings[i], scores[i]) for i in top_idx]
        return results
