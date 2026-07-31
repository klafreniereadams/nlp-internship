from IPython.display import HTML
HTML("""
<style>
div.output_area pre,
div.output_subarea pre,
div.output_text pre {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    max-width: 900px !important;
}
</style>
""")
import os
import time
import pandas as pd
import requests
from semantic_search import SemanticSearcher
from BM_25_search import BM25Searcher
from scipy.stats import spearmanr, kendalltau
from tqdm import tqdm

# Specify paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
REMARKS_PATH = os.path.join(PROJECT_ROOT, "data/processed/listing_remarks.csv")
EMB_PATH = os.path.join(PROJECT_ROOT, "data/processed/remarks_embeddings.npy")

# Instantiate both searchers
searcher = SemanticSearcher(remarks_path=REMARKS_PATH, emb_path=EMB_PATH)
bm25 = BM25Searcher(remarks_path=REMARKS_PATH)

# Load semantic index (never rebuilds here)
if not os.path.exists(searcher.emb_path):
    raise FileNotFoundError(
        f"Embeddings not found at {searcher.emb_path}. "
        "Run the embedding builder script before using this notebook."
    )
searcher.load_index()

# Semantic model warmup
t0 = time.perf_counter()
_ = searcher.model.encode(["warmup"], convert_to_numpy=True)
t1 = time.perf_counter()
print(f"Warmup time: {(t1 - t0) * 1000:.2f} ms")

# Single-query latency test
query = "condo with granite countertops and pool"
t2 = time.perf_counter()
results = searcher.search(query, top_k=10)
t3 = time.perf_counter()
print(f"Post-warmup query latency: {(t3 - t2) * 1000:.2f} ms")

# Full user-experienced latency w/ semantic search
start = time.perf_counter()
with tqdm(total=1, bar_format="{l_bar}{bar}| {elapsed}") as pbar:
    results = searcher.search(query, top_k=10)
    pbar.update(1)
end = time.perf_counter()
print(f"Full semantic query latency: {(end - start) * 1000:.2f} ms")

# Comparison queries
df = pd.read_csv(REMARKS_PATH)
listings = df["remarks"].fillna("").tolist()

queries = [
    "condo with granite countertops and pool",
    "house near good schools with a big backyard",
    "modern townhouse with open floor plan",
    "luxury home with mountain views",
    "starter home under 400k"
]

results = []

for q in queries:
    # BM25 timing
    t0 = time.perf_counter()
    bm25_res = bm25.search(q, top_k=10)
    t1 = time.perf_counter()

    # Semantic timing
    t2 = time.perf_counter()
    sem_res = searcher.search(q, top_k=10)
    t3 = time.perf_counter()

    results.append({
        "query": q,
        "bm25_latency_ms": (t1 - t0) * 1000,
        "semantic_latency_ms": (t3 - t2) * 1000,
        "bm25_top_result": bm25_res[0][0],
        "semantic_top_result": sem_res[0][0]
    })

comparison_df = pd.DataFrame(results)
comparison_df

# -------------------------------------------------------------------------------------------------------
# A strict comparison of latency in ms does not give us real insight into the usefulness of BM25 vs our semantic searcher. 
# A human user will not experience a marked difference between 1 and 399 ms. 
# Where I expect a semantic searcher to really improve a user's experience is in the flexibility and 
# relevance of search results. I compare those more fully below.
# -------------------------------------------------------------------------------------------------------

def show_result(text, score):
    html = f"""
    <div style='max-width:700px; white-space:normal; line-height:1.4; margin-bottom:1em;'>
        <b>Score:</b> {score:.4f}<br>
        {text}
    </div>
    """
    display(HTML(html))

for q in queries:
    print("\n" + "="*80)
    print(f"QUERY: {q}\n")

    bm25_res = bm25.search(q, top_k=2)
    sem_res = searcher.search(q, top_k=2)

    print("BM25 RESULTS:")
    for text, score in bm25_res:
        show_result(text, score)

    print("SEMANTIC RESULTS:")
    for text, score in sem_res:
        show_result(text, score)

# -------------------------------------------------------------------------------------------------------
# A quick Spearman evaluatation and look at overlapping results to heuristically compare 
# top 50 query-relevance pairs of each search method
# -------------------------------------------------------------------------------------------------------

# Spearman
def rank_correlation(bm25_ids, semantic_ids):
    # Build a mapping from listing ID → rank
    bm25_rank = {lid: i for i, lid in enumerate(bm25_ids)}
    semantic_rank = {lid: i for i, lid in enumerate(semantic_ids)}

    # Only compare items that appear in BOTH lists
    overlap = list(set(bm25_ids) & set(semantic_ids))

    bm25_positions = [bm25_rank[lid] for lid in overlap]
    semantic_positions = [semantic_rank[lid] for lid in overlap]

    spearman = spearmanr(bm25_positions, semantic_positions).correlation

    return spearman, overlap

# Overlap
def overlap_metrics(bm25_ids, semantic_ids):
    bm25_set = set(bm25_ids)
    semantic_set = set(semantic_ids)

    intersection = bm25_set & semantic_set
    union = bm25_set | semantic_set

    jaccard = len(intersection) / len(union)
    overlap_count = len(intersection)

    return jaccard, overlap_count, intersection

overlap_matrics()