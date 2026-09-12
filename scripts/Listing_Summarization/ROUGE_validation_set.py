# ROUGE_validation_set.py

# Using Copilot to quickly scan listing_remarks.csv for a 
# varied subset of 20, of which to manually write (human) summaries

import pandas as pd
import re


# Load lising_remarks.csv dataset

df = pd.read_csv("data/processed/listing_remarks.csv")

# Convenience: gets word count for remarks
df["word_count"] = df["L_Remarks"].fillna("").apply(lambda x: len(x.split()))

# Simple amenity detection
amenity_list = ["pool", "solar", "granite", "garage", "fireplace", "yard", "walk-in", "appliances", "flooring", "home office", "theater", "gym", "A/C", "air conditioning","air conditioned", "hoa"]
df["amenity_count"] = df["L_Remarks"].fillna("").apply(
    lambda x: sum(1 for a in amenity_list if a.lower() in x.lower())
)

# ------ Category filters --------

# [short remarks]
short_df = df[df["word_count"] < 40].head(4)

# [medium remarks]
medium_df = df[(df["word_count"] >= 40) & (df["word_count"] <= 120)].head(4)

# [long remarks]
long_df = df[df["word_count"] > 150].head(4)

# [amenity-dense listings]
amenity_df = df[df["amenity_count"] >= 4].head(4)

# [edge-case listings]
def is_edge_case(text):
    if text is None:
        return True
    return (
        text.isupper() or
        bool(re.search(r"\d{5}", text)) or
        len(text.split()) < 10 or
        "..." in text or
        bool(re.search(r"[^\w\s]", text))  # resolves odd punctuation
    )

edge_df = df[df["L_Remarks"].apply(is_edge_case)].head(4)

# Combine listings into final validation set
validation_df = pd.concat([
    short_df,
    medium_df,
    long_df,
    amenity_df,
    edge_df
], ignore_index=True)

# Remove duplicates by remarks text
validation_df = validation_df.drop_duplicates(subset=["L_Remarks"])

if len(validation_df) < 20:
    needed = 20 - len(validation_df)
    filler = df.sample(needed, random_state=42)
    validation_df = pd.concat([validation_df, filler], ignore_index=True)

# 4. Save for inspection
print("Selected 20 validation items:")
print(validation_df[["L_Remarks", "word_count", "amenity_count"]])
validation_df.to_csv("scripts/Listing_Summarization/validation_set.csv", index=False)
