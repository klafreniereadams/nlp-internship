# streamlit_setup.py

import streamlit as st
import requests
import base64

API_BASE = "http://127.0.0.1:8000" # will change to a proper URL

st.set_page_config(page_title="IDX NLP Demo", layout="wide")

# background image
st.markdown(
    """
    <style>
        /* Full-page background */
        .stApp {
            background-image: url("https://your-image-url-here.jpg");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Title formatting
st.markdown(
    """
    <h1 style="font-size: 2.7rem; font-weight: 600;">
        ID<sub>E</sub>Xpert - Intelligent Real Estate Searching
    </h1>
    """,
    unsafe_allow_html=True
)
tabs = st.tabs(["Search", "Metrics"])

with tabs[0]:
    # ---------------------------------------------------------
    # User Input
    # ---------------------------------------------------------
    query = st.text_input("What are you looking for?", "3 bed 2 bath under 700k in Irvine")

    # Run search and store results
    if st.button("Search"):
        parsed = requests.post(f"{API_BASE}/parse-query", json={"query": query}).json()
        response = requests.post(f"{API_BASE}/search", json={"query": query}).json()

        st.session_state["parsed_filters"] = parsed
        st.session_state["search_results"] = response
        st.session_state["selected_listing"] = None  # reset selection


    # ---------------------------------------------------------
    # Show results if they exist
    # ---------------------------------------------------------
    if "search_results" in st.session_state:
        results = st.session_state["search_results"]
        count = results.get("count", 0)

        # First thing a user sees; confirms their query terms
        filters = st.session_state["parsed_filters"].get("filters", {})

        st.markdown("### Got it! Your preferences:")
        st.markdown(
            f"""
            <div style="
                background-color:#f8f9fa;
                padding:15px;
                border-radius:10px;
                border:1px solid #e0e0e0;
                font-size:1rem;
                line-height:1.5;
            ">
                <strong>Max Price:</strong> ${filters.get("price_max", "—"):,.0f}<br>
                <strong>Bedrooms:</strong> {filters.get("bedrooms", "—")}<br>
                <strong>Bathrooms:</strong> {filters.get("bathrooms", "—")}<br>
                <strong>Area:</strong> {filters.get("city", "—")}<br>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.subheader(f"## Found {count} intelligent matches")


        # Two-column layout for search results means less scrolling
        cols = st.columns(2)

        for idx, item in enumerate(results.get("results", [])):
            listing = item["listing"]
            score = item["score"]

            addr = listing["L_Address"]
            city = listing["L_City"]
            beds = listing["beds"]
            baths = listing["baths"]
            price = listing["price"]
            remarks = listing["L_Remarks"]

            # Pick column based on index (0,1,0,1,...)
            col = cols[idx % 2]

            with col:
                with st.container():
                    st.markdown(f"### {addr}, {city}")
                    st.markdown(
                        f"**Price:** ${price:,.0f}  \n"
                        f"**Beds:** {beds} | **Baths:** {baths}"
                    )
                    st.markdown(f"**Semantic Match Score:** {score:.3f}")

                    with st.expander("View Full Remarks"):
                        st.write(remarks)

                    # set both selected listing AND expanded summary index
                    if st.button(f"Summarize listing #{idx+1}", key=f"summarize_{idx}"):
                        st.session_state["selected_listing"] = listing
                        st.session_state["expanded_summary"] = idx

                    # Inline summary now appears directly under this listing
                    if st.session_state.get("expanded_summary") == idx:
                        selected = listing

                        summary_resp = requests.post(
                            f"{API_BASE}/summarize-listing",
                            json={"listing": selected}
                        ).json()

                        # -------------------------------
                        # Prettier summary card
                        # -------------------------------
                        st.markdown("## Listing Summary")

                        st.markdown(
                            f"""
                            <div style="
                                background-color:#f8f9fa;
                                padding:20px;
                                border-radius:10px;
                                border:1px solid #e0e0e0;
                                font-size:1.1rem;
                                line-height:1.5;
                            ">
                                {summary_resp["summary"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Two-column layout for details
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("## Property Details")
                            st.markdown(
                                f"""
                                **Address:** {selected["L_Address"]}, {selected["L_City"]}  
                                **Price:** ${selected["price"]:,.0f}  
                                **Bedrooms:** {selected["beds"]}  
                                **Bathrooms:** {selected["baths"]}  
                                """
                            )

                        with col2:
                            st.markdown("## Property Features")
                            amenities = summary_resp["entities"].get("amenities", [])
                            if amenities:
                                st.markdown(
                                    "<ul style='padding-left:20px;'>"
                                    + "".join([f"<li>{a}</li>" for a in amenities])
                                    + "</ul>",
                                    unsafe_allow_html=True
                                )
                            else:
                                st.write("No amenities detected.")

                    st.markdown("---")

        # ---------------------------------------------------------
        # Prettier Keyword vs Natural Language Search section (w/ collapsible bar)
        # ---------------------------------------------------------

        st.markdown("## 🔍 Keyword vs Natural Language Search")

        # Collapsible comparison section
        with st.expander("Click to compare keyword searching vs natural language searching", expanded=False):

            comparison = requests.post(
                f"{API_BASE}/keyword_search",
                json={"query": query}
            ).json()

            colA, colB = st.columns(2)

            # -------------------------
            # Keyword SQL Column
            # -------------------------
            with colA:
                st.markdown("### Standard Search")

                kw = comparison.get("keyword_result")
                if kw:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#f8f9fa;
                            padding:15px;
                            border-radius:10px;
                            border:1px solid #e0e0e0;
                        ">
                            <strong>Address:</strong> {kw.get("L_Address")}<br>
                            <strong>City:</strong> {kw.get("L_City")}<br>
                            <strong>Beds:</strong> {kw.get("beds")}<br>
                            <strong>Baths:</strong> {kw.get("baths")}<br>
                            <strong>Price:</strong> ${kw.get("price"):,.0f}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.write("No keyword matches found.")

            # -------------------------
            # NLP Semantic Column
            # -------------------------
            with colB:
                st.markdown("### Natural Language Search")

                sm = comparison.get("semantic_result")
                if sm:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:#f8f9fa;
                            padding:15px;
                            border-radius:10px;
                            border:1px solid #e0e0e0;
                        ">
                            <strong>Address:</strong> {sm.get("L_Address")}<br>
                            <strong>City:</strong> {sm.get("L_City")}<br>
                            <strong>Beds:</strong> {sm.get("beds")}<br>
                            <strong>Baths:</strong> {sm.get("baths")}<br>
                            <strong>Price:</strong> ${sm.get("price"):,.0f}<br>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.write("No natural language matches found.")

# Metrics tab
with tabs[1]:
    st.subheader("Metrics")

    metrics = requests.get(f"{API_BASE}/metrics").json()

    total_queries = metrics.get("total_queries", 0)
    avg_latency = metrics.get("avg_latency", 0)
    semantic_accuracy = metrics.get("semantic_accuracy", 0)

    col1, col2, col3 = st.columns(3)

    # lays metrics in a row along the bottom instead of a column
    with col1:
        st.metric("Total Queries", total_queries)
    with col2:
        st.metric("Avg Latency (ms)", avg_latency)
    with col3:
        st.metric("Semantic Accuracy", semantic_accuracy)



# To launch streamlit app:
# streamlit run scripts/Streamlit/streamlit_setup.py
