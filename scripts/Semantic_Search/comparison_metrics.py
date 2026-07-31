# comparison_metrics.py

from semantic_search import SemanticSearcher
from BM_25_search import BM25Searcher
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

REMARKS_PATH = PROJECT_ROOT / "data" / "processed" / "listing_remarks.csv"
EMB_PATH = PROJECT_ROOT / "data" / "processed" / "remarks_embeddings.npy"

searcher = SemanticSearcher(remarks_path=REMARKS_PATH, emb_path=EMB_PATH)
bm25 = BM25Searcher(remarks_path=REMARKS_PATH)
searcher.load_index()

queries = [
    "condo with granite countertops and pool",
    "house near good schools with a big backyard",
    "modern townhouse with open floor plan",
    "luxury home with mountain views",
    "starter home under 400k"
]

def rank_correlation(bm25_ids, semantic_ids):
    bm25_rank = {lid: i for i, lid in enumerate(bm25_ids)}
    semantic_rank = {lid: i for i, lid in enumerate(semantic_ids)}

    overlap = list(set(bm25_ids) & set(semantic_ids))
    if len(overlap) < 2:
        return None, len(overlap)

    bm25_positions = [bm25_rank[lid] for lid in overlap]
    semantic_positions = [semantic_rank[lid] for lid in overlap]

    spearman = spearmanr(bm25_positions, semantic_positions).correlation
    return spearman, len(overlap)

def jaccard_similarity(bm25_ids, semantic_ids):
    bm25_set = set(bm25_ids)
    semantic_set = set(semantic_ids)
    intersection = bm25_set & semantic_set
    union = bm25_set | semantic_set
    return len(intersection) / len(union)

def run_metrics():
    rows = []

    for q in queries:
        bm25_res = bm25.search(q, top_k=50)
        sem_res = searcher.search(q, top_k=50)

        bm25_ids = [text for text, score in bm25_res]
        sem_ids = [text for text, score in sem_res]

        spearman, overlap_count = rank_correlation(bm25_ids, sem_ids)
        jaccard = jaccard_similarity(bm25_ids, sem_ids)

        rows.append({
            "query": q,
            "spearman": None if spearman is None else float(spearman),
            "overlap_count": overlap_count,
            "jaccard": float(jaccard)
        })

    df = pd.DataFrame(rows)
    print(df.to_string(index=False))

if __name__ == "__main__":
    run_metrics()


# ------------------------------------------------------------------------------------
# Metrics show a high rate of overlap between the results returns by BM25 and semantic search
# for 1st, 4th, and 5th query shown. The two methods ranked listings 1 and 5 very differently.
# Very low Jaccard values show that in the top 50 results, BM25 and semantic search are largely
# returning very different listings.
# ------------------------------------------------------------------------------------

#                                query          spearman    overlap_count    jaccard
# condo with granite countertops and pool       -0.586813          14        0.162791
# house near good schools with a big backyard   0.119048           8         0.086957
# modern townhouse with open floor plan         0.085714           14        0.162791
# luxury home with mountain views               0.160714           15        0.176471
# starter home under 400k                       -0.500000          3         0.030928

# Semantic search is clearly prioritizing very different things that BM25's simple key word search. This
# is a good early indication that our semantic search is changing, hopefully improving, over BM25.