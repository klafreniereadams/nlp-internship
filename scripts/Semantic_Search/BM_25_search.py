from rank_bm25 import BM25Okapi
import pandas as pd
import numpy as np
from pathlib import Path

class BM25Searcher:
    def __init__(self, remarks_path=None):
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent

        if remarks_path is None:
            remarks_path = project_root / "data" / "processed" / "listing_remarks.csv"

        print("script_dir:", script_dir)
        print("parent 1:", script_dir.parent)
        print("parent 2:", script_dir.parent.parent)
        print("parent 3:", script_dir.parent.parent.parent)
        print("parent 4:", script_dir.parent.parent.parent.parent)

        df = pd.read_csv(remarks_path)
        self.listings = df["remarks"].fillna("").tolist()

        self.tokenized = [remark.lower().split() for remark in self.listings]
        self.bm25 = BM25Okapi(self.tokenized)

    def search(self, query, top_k=10):
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)

        # Get top_k indices sorted by score descending
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = [(self.listings[i], scores[i]) for i in top_idx]
        return results

bm25 = BM25Searcher()

