import pandas as pd
from entity__
df = pd.read_csv("listing_remarks.csv")

nlp = build_pipeline()   # loads spaCy + both rulers

all_entities = []   # ???

for idx, row in df.iterrows():
    text = row["remarks"]
    doc = nlp(text)

    for ent in doc.ents:
        all_entities.append({
            "row_id": idx,
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })
