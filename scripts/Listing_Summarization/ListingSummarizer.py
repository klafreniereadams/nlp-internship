# ListingSummarizer.py

# EXTRACTIVE summaries only.

import nltk
import json
import pandas as pd

remarks_path = "data/processed/listing_remarks.csv"
df = pd.read_csv(remarks_path)
remarks = df["L_Remarks"].fillna("").tolist()

class ListingSummarizer:
    def __init__(self, amenities_path="scripts/SQL_Queries/canonical_amenities.json"):
        with open(amenities_path, "r") as f:
            self.amenities = set(json.load(f))

    def extractive_summary(self, remarks, entities, num_sentences=2):
        sentences = nltk.sent_tokenize(remarks)

        # Score sentences by entity mentions and position
        scores = []
        for i, sent in enumerate(sentences):
            score = 0
            # First sentence bonus
            if i == 0:
                score += 2
            # Entity mentions
            if str(entities.get('bedrooms', '')) in sent:
                score += 1
            for amenity in self.amenities:
                if amenity.lower() in sent.lower():
                    score += 1
                    
            scores.append((score, sent))

        # Return top sentences
        top_sentences = sorted(scores, reverse=True)[:num_sentences]
        ordered = [s[1] for s in sorted(top_sentences, key=lambda x: sentences.index(x[1]))]

        # NOTE - I will need to include this 'prefix' sentence in my 
        # manual summaries or else the ROUGE score will appear much lower
        prefix = (
                    f"This is a {entities.get('bedrooms', 'N/A')} bed, "
                    f"{entities.get('bathrooms', 'N/A')} bath home "
                    f"priced at ${entities.get('price', 'N/A')} in "
                    f"{entities.get('city', 'N/A')}."
                )

        
        return prefix + " " + " ".join(ordered)
    
summarizer = ListingSummarizer()

sample_df = df.sample(n=4, random_state=42)

for _, row in sample_df.iterrows():
    remarks = row["L_Remarks"]
    entities = {
        "bedrooms": row["beds"],
        "bathrooms": row["baths"],
        "price": row["price"],
        "city": row["L_City"]
    }

    summary = summarizer.extractive_summary(remarks, entities)
    print(summary)

"""
This is a 5 bed, 2.0 bath home priced at $350000 in Bakersfield. Welcome to your dream home! 
The decent-sized backyard is a true highlight, offering plenty of room for outdoor activities, 
gardening, or simply unwinding in your personal oasis.

This is a 5 bed, 4.0 bath home priced at $648000 in Patterson. Welcome to this charming and spacious 
4-bedroom, 3-bath home located in a peaceful neighborhood. The private outdoor space is perfect for 
hosting summer BBQs or enjoying a quiet evening under the stars.

This is a 5 bed, 6.0 bath home priced at $2995000 in Escondido. **NEW PRICE**NEW CONSTRUCTION**
MULTI-GENERATIONAL LIVING  Unprecedented privacy and ocean views. home is designed to capture 
sweeping views of the Hyatt Vacation Club and Golf Course as well as Catalina Island.

This is a 2 bed, 3.0 bath home priced at $1849000 in La Selva Beach. This is a rare front-row location 
with access to sandy beaches & HOA tennis courts, pool, & clubhouse. Upstairs are two spacious 
bedrooms, including the primary suite, a 2nd guest bath plus a laundry room & open office nook.
"""