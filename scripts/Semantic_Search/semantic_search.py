import time
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd

# Load all listing remarks
df = pd.read_csv("data/processed/listing_remarks.csv")
remarks = df["remarks"].fillna("").tolist()

class SemanticSearcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.listings = None
    
    def build_index(self, remarks_list):
        print(f"Encoding {len(remarks_list)} listings...")
        embeddings = self.model.encode(remarks_list)
    
        # Normalize dimensions (cosine similarity)
        faiss.normalize_L2(embeddings)
    
        # Build FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        self.listings = remarks_list

    # Inner product for cosine sim
    def search(self, query, top_k=10):
        query_emb = self.model.encode([query])
        faiss.normalize_L2(query_emb)

        scores, indices = self.index.search(query_emb, top_k)
        results = [(self.listings[i], scores[0][j]) for j, i in enumerate(indices[0])]
        return results
    
# Build semantic search index
searcher = SemanticSearcher()
searcher.build_index(remarks)

# Sample query and latency of full user-experienced latency
query = "condo with granite countertops and pool"

start = time.perf_counter()
with tqdm(total=1, bar_format="{l_bar}{bar}| {elapsed}") as pbar:
    results = searcher.search(query, top_k=10)
    pbar.update(1)

end = time.perf_counter()
latency_ms = (end - start) * 1000
print(f"Full query latency: {latency_ms:.2f} ms")