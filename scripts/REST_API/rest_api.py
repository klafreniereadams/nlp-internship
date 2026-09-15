# rest_api.py
# imports from app_setup.py

from fastapi import HTTPException, FastAPI, Depends
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel
from scripts.Semantic_Search.filtering import apply_filters
from .app_setup import cache_get, cache_set, db_conn

# Import the initialized NLP components
import scripts.REST_API.app_setup as setup
app = setup.app

#from scripts.REST_API.app_setup import (
    #app,
    #query_parser,
    #semantic_searcher,
    #entity_extractor,
    #summarizer,
    #compliance_checker
#)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class SearchResponse(BaseModel):
    query: str
    results: list
    count: int


@app.post("/search", response_model=SearchResponse, dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def search_listings(request: SearchRequest):
    cache_key = f"search:{request.query}:{request.top_k}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    # parse filters from natural language
    filters = setup.query_parser.parse(request.query)
    # semantic search returns structured listings
    semantic_results = setup.semantic_searcher.search(request.query, request.top_k)

    # re-apply structured filters after demo
    results = semantic_results
    #results = apply_filters(semantic_results)
    #results = apply_filters(semantic_results, filters)

    response = SearchResponse(
        query=request.query,
        results=results,
        count=len(results)
    )

    await cache_set(cache_key, response.model_dump())
    return response


@app.post("/parse-query")
async def parse_query(request: SearchRequest):
    filters = setup.query_parser.parse(request.query)
    return {"query": request.query, "filters": filters}


@app.post("/summarize")
async def summarize_listing(request: SearchRequest):
    # Run semantic search to get the top listing
    semantic_results = setup.semantic_searcher.search(request.query, top_k=1)

    if not semantic_results:
        raise HTTPException(status_code=404, detail="No listings found")

    listing = semantic_results[0]["listing"]

    remarks = listing["L_Remarks"]
    doc = setup.entity_extractor(remarks)

    # # Convert spaCy entities into the dict format your summarizer expects
    # entities = {
    #     "bedrooms": None,
    #     "bathrooms": None,
    #     "price": None,
    #     "city": None
    # }

    # use listing fields instead of spaCY for demo
    entities = {
        "bedrooms": listing.get("beds"),
        "bathrooms": listing.get("baths"),
        "price": listing.get("price"),
        "city": listing.get("L_City")
}

    for ent in doc.ents:
        if ent.label_ == "BEDROOMS":
            entities["bedrooms"] = ent.text
        elif ent.label_ == "BATHROOMS":
            entities["bathrooms"] = ent.text
        elif ent.label_ == "PRICE":
            entities["price"] = ent.text
        # AMENITY and SQFT are access separately

    summary = setup.summarizer.extractive_summary(remarks, entities)
    return {
        "query": request.query,
        "summary": summary,
        "listing": listing,
        "entities": entities
    }

@app.post("/entities")
async def extract_entities(request: SearchRequest):
    # Run semantic search to get the top listing
    semantic_results = setup.semantic_searcher.search(request.query, top_k=1)

    if not semantic_results:
        raise HTTPException(status_code=404, detail="No listings found")

    listing = semantic_results[0]["listing"]

    remarks = listing["remarks"]
    doc = setup.entity_extractor(remarks)

    # Convert spaCy entities into a simple dict
    entities = {
        "bedrooms": None,
        "bathrooms": None,
        "price": None,
        "sqft": None,
        "amenities": []
    }

    for ent in doc.ents:
        if ent.label_ == "BEDROOMS":
            entities["bedrooms"] = ent.text
        elif ent.label_ == "BATHROOMS":
            entities["bathrooms"] = ent.text
        elif ent.label_ == "PRICE":
            entities["price"] = ent.text
        elif ent.label_ == "SQFT":
            entities["sqft"] = ent.text
        elif ent.label_ == "AMENITY":
            entities["amenities"].append(ent.text)

    return {
        "query": request.query,
        "entities": entities,
        "listing": listing
    }

@app.post("/compliance")
async def check_compliance(request: SearchRequest):
    # Run semantic search to get the top listing
    semantic_results = setup.semantic_searcher.search(request.query, top_k=1)

    if not semantic_results:
        raise HTTPException(status_code=404, detail="No listings found")

    listing = semantic_results[0]["listing"]

    # Run compliance check on the listing
    compliance_result = setup.compliance_checker.check(listing)

    return {
        "query": request.query,
        "compliance": compliance_result,
        "listing": listing
    }

# ----------------------------------------------------------------------------
# this optional function within the appl will let a user expand their 
# search to wider results outside their ideals. Combines BM25, 
# semantic, and SQL searching 
# ----------------------------------------------------------------------------
@app.post("/search-broad")
async def search_broad(request: SearchRequest):
    query = request.query
    filters = setup.query_parser.parse(query)

    # 1. Semantic search
    semantic_results = setup.semantic_searcher.search(query, request.top_k)

    # 2. BM25 search
    try:
        from scripts.Semantic_Search.BM_25_search import bm25_search
        bm25_results = bm25_search(query, request.top_k)
    except Exception:
        bm25_results = []

    # 3. SQL search
    try:
        sql_query, params = setup.query_parser.to_sql(filters)
        with db_conn.cursor() as cur:
            cur.execute(sql_query, params)
            sql_rows = cur.fetchall()
        sql_results = [dict(row) for row in sql_rows]
    except Exception:
        sql_results = []

    # 4. Merge + dedupe
    combined = {}

    # semantic
    for r in semantic_results:
        listing_id = r["listing"].get("id")
        combined[listing_id] = {
            "listing": r["listing"],
            "semantic_score": r["score"],
            "bm25_score": 0,
            "sql_match": False
        }

    # bm25
    for r in bm25_results:
        listing_id = r["listing"].get("id")
        if listing_id not in combined:
            combined[listing_id] = {
                "listing": r["listing"],
                "semantic_score": 0,
                "bm25_score": r["score"],
                "sql_match": False
            }
        else:
            combined[listing_id]["bm25_score"] = r["score"]

    # sql
    for row in sql_results:
        listing_id = row.get("id")
        if listing_id not in combined:
            combined[listing_id] = {
                "listing": row,
                "semantic_score": 0,
                "bm25_score": 0,
                "sql_match": True
            }
        else:
            combined[listing_id]["sql_match"] = True

    # 5. Hybrid ranking
    final_results = sorted(
        combined.values(),
        key=lambda x: (
            x["semantic_score"] * 0.6 +
            x["bm25_score"] * 0.3 +
            (1 if x["sql_match"] else 0) * 0.1
        ),
        reverse=True
    )

    return {
        "query": query,
        "filters": filters,
        "results": final_results,
        "count": len(final_results)
    }
# ----------------------------------------------------------------------------

# not really for the user, but industry standard for APIs
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/version")
async def version():
    return {"version": "1.0.0"}

# for future debugging maybe
@app.get("/endpoints")
async def list_endpoints():
    return {
        "available_endpoints": [
            "/search",
            "/parse-query",
            "/summarize",
            "/entities",
            "/compliance",
            "/search-broad",
            "/health"
        ]
    }

class ListingPayload(BaseModel):
    listing: dict

@app.post("/summarize-listing")
async def summarize_specific_listing(payload: ListingPayload):
    listing = payload.listing

    remarks = listing.get("L_Remarks", "")
    doc = setup.entity_extractor(remarks)

    entities = {
        "bedrooms": listing.get("beds"),
        "bathrooms": listing.get("baths"),
        "price": listing.get("price"),
        "city": listing.get("L_City"),
        "amenities": []
    }

    for ent in doc.ents:
        if ent.label_ == "BEDROOMS":
            entities["bedrooms"] = ent.text
        elif ent.label_ == "BATHROOMS":
            entities["bathrooms"] = ent.text
        elif ent.label_ == "PRICE":
            entities["price"] = ent.text
        elif ent.label_ == "AMENITY":
            entities["amenities"].append(ent.text)

    summary = setup.summarizer.extractive_summary(remarks, entities)

    return {
        "summary": summary,
        "listing": listing,
        "entities": entities
    }

"""
Launching the API:

docker compose up -d
docker ps
docker run -d --name redis -p 6379:6379 redis
or docker start redis

lsof -i :8000 # checks what's active on port 8000
take note of the PID(second column) of the thing present there.
kill [PID]
then run:
uvicorn scripts.REST_API.rest_api:app --reload
http://127.0.0.1:8000/docs

"""