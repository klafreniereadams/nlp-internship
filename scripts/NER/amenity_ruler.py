import json
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler

def construct_amenity_ruler(nlp, processed/taxonomy.json):
    with open(processed/taxonomy.json, 'r') as f:
        amenities = json.load(f)

    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    for amenity in amenities:
        patterns.append({"label": "AMENITY", "pattern": amenity})
    ruler.add_patterns(patterns)
    return nlp

nlp = spacy.load("en_core_web_sm")
nlp = construct_amentity_ruler(nlp, 'processed/taxonomy.json')


# Apply to the listing_remarks.csv data
df = pd.read_csv("listing_remarks.csv")

nlp = spacy.load("en_core_web_sm")
nlp = construct_amenity_ruler(nlp, "taxonomy.json")

all_spans = []

for idx, row in df.iterrows():
    text = row["remarks"]
    doc = nlp(text)

    for ent in doc.ents:
        all_spans.append({
            "row_id": idx,
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })