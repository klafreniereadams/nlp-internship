# streamlit_setup.py

import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000" # will change to a proper URL

st.set_page_config(page_title="IDX NLP Demo", layout="wide")

st.title("Real Estate Intelligent Search")
st.write("Natural language → parsed filters → semantic search → summaries → details")

# ---------------------------------------------------------
# User Input
# ---------------------------------------------------------
query = st.text_input("What are you looking for?", "3 bed 2 bath under 700k in Irvine")

if st.button("Search"):
    if not query:
        st.warning("Please enter a valid query")
        st.stop()

    # 1. Parsed filters
    parsed = requests.post(f"{API_BASE}/parse-query", json={"query": query}).json()
    st.subheader("Parsed Filters")
    st.json(parsed)

    # 2. Semantic search
    response = requests.post(f"{API_BASE}/search",json={"query": query})
    results = response.json()
    count = results.get("count", 0)
    st.subheader(f"Found {count} intelligent matches")

    for item in results.get("results", []):
        listing = item["listing"]
        score = item["score"]

        addr = listing["L_Address"]
        city = listing["L_City"]
        beds = listing["beds"]
        baths = listing["baths"]
        price = listing["price"]
        remarks = listing["L_Remarks"]

        with st.container():
            st.markdown(f"**{addr }, {city}**")
            st.markdown(
                f"**Price:** ${price:,.0f} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"**Beds:** {beds} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"**Baths:** {baths}"
            )
            st.markdown(f"**Semantic Match Score:** {score:.3f}")

            with st.expander("View Remarks"):
                st.write(remarks)

            st.markdown("---")


    # 3. Summaries
    summaries = requests.post(
        f"{API_BASE}/summarize",
        json={"query": query}
    ).json()

    st.subheader("Listing Summary")
    st.write(summaries["summary"])
    st.write("---")
    st.subheader("Details")
    st.json(summaries["listing"])
    st.subheader("Amenities")
    st.json(summaries["entities"])

    # 4. Keyword search comparison
    st.subheader("Keyword SQL vs NLP Semantic Search")
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Keyword Search")
        keyword = requests.post(f"{API_BASE}/keyword_search", json={"query": query}).json()
        st.json(keyword)

    with col2:
        st.write("### NLP Semantic Search")
        st.json(results)

    # 5. Metrics
    st.subheader("Metrics")

    metrics = requests.get(f"{API_BASE}/metrics").json()

    total_queries = metrics.get("total_queries", 0)
    avg_latency = metrics.get("avg_latency", 0)
    semantic_accuracy = metrics.get("semantic_accuracy", 0)

    st.metric("Total Queries", total_queries)
    st.metric("Avg Latency (ms)", avg_latency)
    st.metric("Semantic Accuracy", semantic_accuracy)


""" To launch streamlit app:
streamlit run scripts/Streamlit/streamlit_setup.py


"""