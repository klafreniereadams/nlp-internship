import json
import spacy
from termcolor import colored
from entity_extraction import add_entity_extractor
import os

# ---------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------
def build_pipeline():
    nlp = spacy.load("en_core_web_sm")
    nlp = add_entity_extractor(nlp, "data/processed/taxonomy.json")
    return nlp

nlp = build_pipeline()

# ---------------------------------------------------------
# Load machine‑labeled dataset
# ---------------------------------------------------------
with open("scripts/NER/labeled_entity_dataset.json") as f:
    data = json.load(f)

# ---------------------------------------------------------
# Load existing gold file if it exists
# ---------------------------------------------------------
gold_path = "scripts/NER/gold_corrected.json"
if os.path.exists(gold_path):
    with open(gold_path) as f:
        gold = json.load(f)
else:
    gold = []

# Track which texts are already labeled
already_done = {entry["text"] for entry in gold}

# ---------------------------------------------------------
# Helper to highlight a single span
# ---------------------------------------------------------
def highlight_single(text, span):
    s, e = span["start"], span["end"]
    return text[:s] + colored(text[s:e], "cyan") + text[e:]

# ---------------------------------------------------------
# Annotation loop (resumable)
# ---------------------------------------------------------
for item in data:
    text = item["text"]

    # Skip if already labeled
    if text in already_done:
        continue

    doc = nlp(text)
    preds = [
        {"start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]

    gold_spans = []

    print("\n" + "="*80)
    print("NEW LISTING:")
    print(text)
    print("="*80)

    for i, span in enumerate(preds):
        print(f"\nPredicted entity {i+1}/{len(preds)}:")
        print(highlight_single(text, span))
        print("Prediction:", span)

        while True:
            cmd = input("[a]ccept / [e]dit / [s]kip: ").strip().lower()

            if cmd == "a":
                gold_spans.append(span)
                break

            elif cmd == "e":
                substring = input("Exact substring: ").strip()
                label = input("Label (AMENITY/BEDROOMS/BATHROOMS/PRICE/SQFT): ").strip().upper()

                start = text.lower().find(substring.lower())
                if start == -1:
                    print("Substring not found.")
                    continue

                end = start + len(substring)
                gold_spans.append({"start": start, "end": end, "label": label})
                break

            elif cmd == "s":
                break

    # Add missing spans
    while True:
        cmd = input("Add missing span? [y/n]: ").strip().lower()
        if cmd == "n":
            break
        if cmd == "y":
            substring = input("Exact substring: ").strip()
            label = input("Label: ").strip().upper()
            start = text.lower().find(substring.lower())
            if start == -1:
                print("Substring not found.")
                continue
            end = start + len(substring)
            gold_spans.append({"start": start, "end": end, "label": label})

    gold.append({"text": text, "entities": gold_spans})

    # Save progress after each listing
    with open(gold_path, "w") as f:
        json.dump(gold, f, indent=2)

    print(f"Saved progress to {gold_path}")

print("\nAll done.")
