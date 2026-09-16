## 2026 NLP Internship

# A production-ready NLP system for real estate listings. Produces a REST API exposing: search, entity extraction, query parsing, and summarization.

# Database consists of three MySQL tables of genuine California real estate data provided by IDX Exhange in February 2026:
# * rets_property: Active/pending listings with remarks, pricing, features
# * rets_openhouse: Open house schedules and details
# * california_sold: Historical sold properties with transaction data


# The system demonstrates how modern NLP techniques allow querying in natural language, ultimately outperforming traditional keyword/BM25/SQL search techniques. 

# Semantic search using embeddings + FAISS
# Baseline BM25 + SQL search
# NLP extraction (NER, POS, dependency parsing)
# Buyer intent classification and US Fair Housing Act compliance checking
# FastAPI backend
# Streamlit frontend
# Redis rate limiting

## Project Architecture

                ┌───────────────────────-───┐
                │        Streamlit UI       │
                │  - Query input            │
                │  - Results comparison     │
                │  - Summaries              │
                └─────────────┬─────────-───┘
                              │
                              ▼
                ┌──────────────────────────-┐
                │      FastAPI Backend      │
                │  - Query parsing          │
                │  - SQL/BM25 search        │
                │  - Semantic search        │
                │  - NLP modules            │
                └─────────────┬──────────-──┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────--──┐     ┌────────────────┐     ┌────────────────-──┐
│ MySQL DB      │     │ FAISS Index    │     │ NLP Modules       │
│ MLS listings  │     │ Embeddings     │     │ NER, POS, parsing │
└───────────-───┘     └────────────────┘     └───────────────-───┘

## Repository structure

nlp-internship/
    cleanenv/
    data/
    notebooks/
    scripts/
        Buyer_Intent/
        Data_Preparation/
        Fair_Housing_Compliance/
        Listing_Summarization/
        NER/
        REST_API/
            rest_api.py
            app_setup.py
        Semantic_Search/
            semantic_search.py
        Signal_Extraction/
        SQL_Queries/
        Streamlit/
    tests/


# The final user experience:
# Natural language query → NLP parsing → SQL filters → semantic search → side‑by‑side comparison + summaries


## Local setup instructions
# 1. Clone the repository
git clone <your-repo-url>
cd nlp-internship

# 2. Create a clean pip environment
python -m venv cleanenv

# 3. Activate the environment
# macOS/Linux:
source cleanenv/bin/activate
# Windows (PowerShell):
cleanenv\Scripts\Activate.ps1
# Windows (CMD):
cleanenv\Scripts\activate.bat

# 4. Install dependencies
pip install -r requirements.txt

# 5. Ensure MySQL is running with the MLS tables:
rets_property, rets_openhouse, california_sold

# (Optional) Install FAISS locally via Conda if needed
# macOS cannot install FAISS via pip

# 6. Start the FastAPI backend
uvicorn scripts.REST_API.rest_api:app --reload

# 7. Start the Streamlit frontend
streamlit run scripts/Streamlit/app.py

# Full deployment instructions to be updated in late 2026