# app_setup.py
# code scaffolding provided by IDX Exchange, fleshed out with the help 
# of guided copilot

import json
import spacy
import mysql.connector
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from pathlib import Path
from contextlib import asynccontextmanager
from redis.asyncio import Redis

# 1) Import NLP components from each week's work
from scripts.SQL_Queries.query_parser import QueryParser
from scripts.Semantic_Search.semantic_search import SemanticSearcher
from scripts.NER.entity_extraction import add_entity_extractor
# from scripts.Signal_Extraction.signal_extraction import SignalExtractor - not for user
from scripts.Listing_Summarization.ListingSummarizer import ListingSummarizer
# from scripts.Buyer_Intent.intent_classifier import IntentClassifier - not for user
from scripts.Fair_Housing_Compliance.ComplianceChecker import ComplianceChecker

# 2) global objects that are loaded only once at startup for efficiency
query_parser = None
semantic_searcher = None
entity_extractor = None
summarizer = None
compliance_checker = None

db_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="real_estate"
)
db_conn.autocommit = True

# Caching with Redis
redis_client = Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

async def cache_get(key: str):
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None

async def cache_set(key: str, value: dict, ttl: int = 60):
    await redis_client.set(key, json.dumps(value), ex=ttl)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(redis_client)
    global query_parser, semantic_searcher
    global entity_extractor, summarizer, compliance_checker

    amenities_path = Path("scripts/SQL_Queries/canonical_amenities.json")

    # Initialize heavy NLP components only once
    query_parser = QueryParser(amenities_path)
    semantic_searcher = SemanticSearcher()
    semantic_searcher.load_index()

    # Initialize spaCy + entity extractor pipeline
    taxonomy_path = Path("scripts/SQL_Queries/canonical_amenities.json")
    nlp = spacy.load("en_core_web_sm")
    nlp = add_entity_extractor(nlp, taxonomy_path)
    entity_extractor = nlp

    summarizer = ListingSummarizer()
    compliance_checker = ComplianceChecker()

    yield

# -------------------------------------------------------------------------
# This creates the NLP objects that will be exposed
app = FastAPI(
    title="Real Estate NLP API",
    lifespan=lifespan,
    description="Semantic, BM25, and SQL hybrid search",
    version="1.0.0"
)