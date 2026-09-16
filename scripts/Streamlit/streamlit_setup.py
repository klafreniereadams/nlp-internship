# streamlit_setup.py

import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000" # will change to a proper URL

st.set_page_config(page_title="IDX NLP Demo", layout="wide")

# background color
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f7f3e9; /* soft cream */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title formatting
st.markdown(
    """
<link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap" rel="stylesheet">
    """,
        unsafe_allow_html=True
)
st.markdown(
       """
    <style>
        .main-title {
            font-family: 'Quicksand', sans-serif;
            font-size: 48px;
            font-weight: 600;
            text-align: center;
            color: #3a3a3a;
            margin-bottom: -10px;
        }

        .subtitle {
            font-family: 'Quicksand', sans-serif;
            font-size: 22px;
            font-weight: 400;
            text-align: center;
            color: #6e6e6e;
            margin-top: 0px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("<div class='main-title'>ID<sub>E</sub>XPERT</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Smarter Search for Real Estate</div>", unsafe_allow_html=True)

# Regular text
st.markdown(
    """
    <style>
        /* Increase general text size */
        html, body, p, span, div {
            font-size: 24px;
        }

        /* Optional: make Streamlit widgets match */
        .stMarkdown, .stTextInput, .stSelectbox, .stMultiSelect, .stButton {
            font-size: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
tabs = st.tabs(["Search", "Keyword vs Natural Language Search", "Metrics"])

with tabs[0]:
    # ---------------------------------------------------------
    # User Input
    # ---------------------------------------------------------
    query = st.text_input("What are you looking for?", placeholder="e.g., 3 bed 2 bath home under 700k in Irvine")

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

        st.markdown("### Your preferences:")
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
                <strong>Max Price:</strong> ${f"{filters['price_max']:,.0f}" if isinstance(filters.get("price_max"), (int, float)) else "—"}<br>
                <strong>Bedrooms:</strong> {filters.get("bedrooms", "—")}<br>
                <strong>Bathrooms:</strong> {filters.get("bathrooms", "—")}<br>
                <strong>Area:</strong> {filters.get("city", "—")}<br>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.subheader(f"Found {count} intelligent matches")


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

                    if st.button(f"Summarize listing #{idx+1}", key=f"summarize_{idx}"):

                        # If this listing is already expanded → collapse it
                        if st.session_state.get("expanded_summary") == idx:
                            st.session_state["expanded_summary"] = None
                            st.session_state["selected_listing"] = None

                        # Otherwise → expand it
                        else:
                            st.session_state["expanded_summary"] = idx
                            st.session_state["selected_listing"] = listing


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

with tabs[1]:
    st.subheader("Keyword vs Natural Language Search")

    # Explanation block
    st.markdown(
        """
        <div style="
            background-color:#f8f9fa;
            padding:15px;
            border-radius:10px;
            border:1px solid #e0e0e0;
            font-size:18px;
            margin-bottom:20px;
        ">
            <strong>Standard Search</strong> matches exact words or phrases in the listing data.<br>
            <strong>Natural Language Search</strong> interprets meaning, intent, and context.
        </div>
        """,
        unsafe_allow_html=True
    )
    # -----------------------------------------
    # User test search box
    # -----------------------------------------
    st.markdown(
        """
        <div style="
            font-size:18px;
            margin-top:10px;
            margin-bottom:5px;
        ">
            Try it yourself — enter a search and compare how each method responds:
        </div>
        """,
        unsafe_allow_html=True
    )

    user_test_query = st.text_input(
        "Test Search",
        placeholder="e.g., homes with a big yard near Escondido",
        value=query if query else ""
    )
    if user_test_query:
        test_results = requests.post(
            f"{API_BASE}/compare_search",
            json={"query": user_test_query}
        ).json()

        col1, col2 = st.columns(2)

        # # Fetch comparison results
        # comparison = requests.post(
        # f"{API_BASE}/compare_search",
        # json={"query": query}).json()

        # -------------------------
        # Condensed Keyword Result
        # -------------------------
        with col1:
            st.markdown("#### Standard Search Results")

            kw = test_results.get("keyword_result")
            if kw:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#ffffff;
                        padding:12px;
                        border-radius:10px;
                        border:1px solid #e0e0e0;
                        font-size:17px;
                    ">
                        <strong>{kw.get("L_Address")}</strong><br>
                        {kw.get("L_City")}<br>
                        {kw.get("beds")} beds • {kw.get("baths")} baths<br>
                        ${kw.get("price"):,.0f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.write("No keyword matches found.")

        # -------------------------
        # Condensed NLP Result
        # -------------------------
        with col2:
            st.markdown("#### Natural Language Result")

            # Fudged NLP search → reuse regular search endpoint
            nlp_results = requests.post(
                f"{API_BASE}/search",
                json={"query": user_test_query}
            ).json()

            if not nlp_results.get("results"):
                st.write("No natural language matches found.")
            else:
                # Use the FIRST result for the demo
                listing = nlp_results["results"][0]["listing"]
                score = nlp_results["results"][0].get("score", 0)

                addr = listing["L_Address"]
                city = listing["L_City"]
                beds = listing["beds"]
                baths = listing["baths"]
                price = listing["price"]
                remarks = listing["L_Remarks"]

                # Summary card (same style as regular search)
                st.markdown(f"### {addr}, {city}")
                st.markdown(
                    f"**Price:** ${price:,.0f}  \n"
                    f"**Beds:** {beds} | **Baths:** {baths}"
                )
                st.markdown(f"**Semantic Match Score:** {score:.3f}")

                # Collapsible remarks
                with st.expander("View Full Remarks"):
                    st.write(remarks)

                # Summary button
                if st.button("Summarize this listing", key="nlp_summarize"):
                    # Toggle expanded summary
                    if st.session_state.get("nlp_expanded_summary"):
                        st.session_state["nlp_expanded_summary"] = False
                    else:
                        st.session_state["nlp_expanded_summary"] = True
                        st.session_state["nlp_selected_listing"] = listing

                # Expanded summary card
                if st.session_state.get("nlp_expanded_summary"):
                    selected = st.session_state["nlp_selected_listing"]

                    summary_resp = requests.post(
                        f"{API_BASE}/summarize-listing",
                        json={"listing": selected}
                    ).json()

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
                                 
        colA, colB = st.columns(2)


# Metrics tab
with tabs[2]:
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
