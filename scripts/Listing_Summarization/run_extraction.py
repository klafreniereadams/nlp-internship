# run_extraction.py

# generated with Copilot and edited for personalization

import pandas as pd
from ListingSummarizer import ListingSummarizer

# Load the human validation set
df = pd.read_csv("scripts/Listing_Summarization/human_validation_set.csv")

summarizer = ListingSummarizer()

# Generates extractive summaries via ListingSummarizer.py
model_summaries = []
for _, row in df.iterrows():
    remarks = row["L_Remarks"]

    # I am only extracting from L_Remarks; in the validation set,
    # those select listings don't include price. The listings frequently
    # include bed and bath, but I'll have to be content with the model
    # summaries missing that information.
    entities = {
        "bedrooms": row.get("beds", "N/A"),
        "bathrooms": row.get("baths", "N/A"),
        "price": row.get("price", "N/A"),
        "city": row.get("L_City", "N/A")
    }

    summary = summarizer.extractive_summary(remarks, entities)
    model_summaries.append(summary)

df["Model_Summary"] = model_summaries

# Save back to the same file
df.to_csv("scripts/Listing_Summarization/human_validation_set.csv", index=False)
