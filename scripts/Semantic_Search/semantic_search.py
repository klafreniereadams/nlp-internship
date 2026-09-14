# semantic_search.py

import os
# I tinkered with the thread number to decrease latency at the encoding step with sentence_transformer on my machine
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"
import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd

# Load the listing remarks, create embeddings, cache as .npy file
class SemanticSearcher:
    def __init__(self, emb_path="data/processed/remarks_embeddings.npy",
                 remarks_path="data/processed/listing_remarks.csv"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.listings = None
        self.emb_path = emb_path
        self.remarks_path = remarks_path
    
    def build_index(self):
        df = pd.read_csv(self.remarks_path)
        self.df = df
        self.listings = df["remarks"].fillna("").tolist()

        # If cached embeddings exist, load them now
        if os.path.exists(self.emb_path):
            embeddings = np.load(self.emb_path)
            print(f"Loaded cached embeddings: {embeddings.shape}")
        else:
            print(f"Encoding {len(self.listings)} listings...")
            embeddings = self.model.encode(self.listings, convert_to_numpy=True)
            faiss.normalize_L2(embeddings)
            np.save(self.emb_path, embeddings)
            print(f"Saved embeddings to {self.emb_path}")
    
        # Build FAISS index for the first time
        dim = embeddings.shape[1]
        # exact search, no compression or approximation
        # when scaling up to 1M listings, flat index might be less ideal
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

    def load_index(self):
        if not os.path.exists(self.emb_path):
            raise FileNotFoundError(f"Embeddings not found at {self.emb_path}")

        embeddings = np.load(self.emb_path)
        # Ensure cached embeddings are ALSO normalized, to keep latency lower
        faiss.normalize_L2(embeddings)
        print(f"Loaded cached embeddings: {embeddings.shape}")

        df = pd.read_csv(self.remarks_path)
        self.listings = df["remarks"].fillna("").tolist()
        print(f"Loaded {len(self.listings)} listing remarks")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        print("FAISS index rebuilt from cached data")

    # Inner product for cosine sim
    def search(self, query, top_k=10):
        query_emb = self.model.encode([query])
        faiss.normalize_L2(query_emb)

        scores, indices = self.index.search(query_emb, top_k)

        results = []
        for rank, idx in enumerate(indices[0]):
            row = self.df.iloc[idx].to_dict()
            results.append({
                "listing": row,
                "score": float(scores[0][rank])
            })
        return results