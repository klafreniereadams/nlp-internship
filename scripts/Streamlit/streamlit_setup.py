# streamlit_setup.py

import streamlit as st
import requests
st.title("Real Estate Intelligent Search")
query = st.text_input("What are you looking for?", "3 bed 2 bath under 700k in Irvine")
if st.button("Search"):
    response = requests.post("http://localhost:8000/search", json={"query":query})
    results = response.json()
    st.write(f"Found {results['count']} listings")
    for listing in results['results']:
        st.subheader(listing['address'])
        st.write(f"Price: ${listing['price']:,}")
        st.write(f"Summary: {listing['summary']}")
        st.write("---")