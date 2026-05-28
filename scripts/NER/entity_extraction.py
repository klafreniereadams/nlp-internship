import os; print("CWD:", os.getcwd())
import re
import csv
import pandas as pd
import json
import spacy
from spacy.language import Language
from spacy.util import filter_spans
from spacy.tokens import Span

# taxonomy.json  ---> load inside EntityExtractor.__init__
# listing_remarks.csv ---> load outside the class, row by row
# SpaCy pipeline ---> receives each remark as doc.text

@Language.factory("entity_extractor")
def create_entity_extractor(nlp, name, taxonomy_path):
    return EntityExtractor(nlp, taxonomy_path)

# set up pipeline so python will run the extractor on every doc
def add_entity_extractor(nlp, taxonomy_path):
    nlp.add_pipe("entity_extractor", config={"taxonomy_path": taxonomy_path})
    return nlp


class EntityExtractor:
    def __init__(self, nlp, taxonomy_path):
        self.nlp = nlp

        # load taxonomy and format its content for pattern matching
        # will detect raw n-gram "amenities" identified during text_cleaning
        with open (taxonomy_path, "r") as f:
            taxonomy = json.load(f)
        self.amenities = [t["term"] for t in taxonomy["terms"]]

        # ----------------------------------------------------------------------------
        # Define regex patterns
        # ----------------------------------------------------------------------------
        self.bedroom_patterns = [
            r'(\d+)\s*(?:bed|br|bedroom)s?',
            r'(\d+)bd'
        ]

        self.bathroom_patterns = [
            r'(\d+(\.\d+)?)\s*(?:bath|ba|bathroom)s?',
            r'(\d+(\.\d+)?)\s*ba'
        ]

        self.price_patterns = [
            r'\$?(\d{5,})'
        ]

        self.sqft_patterns = [
            r'(\d{3,})\s*(sq\s*\.?\s*ft|sqft|sq\.?ft\.?)'
        ]
    
    # ----------------------------------------------------------------------------
    # the extraction functions below assume cleaned text from week 2
    # ----------------------------------------------------------------------------
    
    def extract_bedrooms(self, text):
        for pattern in self.bedroom_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1)
        return None
    
    def extract_bathrooms(self, text):
        for pattern in self.bathroom_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(1)
        return None

    def extract_price(self, text):
        for pattern in self.price_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return float(match.group(1))
        return None
    
    def extract_sqft(self, text):
        for pattern in self.sqft_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return float(match.group(1))
        return None
    
    #def extract_all(self, text):
        #return {
            #'bedrooms': self.extract_bedrooms(text),
            #'bathrooms': self.extract_bathrooms(text),
            #'price': self.extract_price(text),
            #'sqft': self.extract_sqft(text),
            #'amenities': self.extract_amenities(text)}

    # ----------------------------------------------------------------------------
    # Assemble all pertinent specs from listing_remarks.py 
    # ----------------------------------------------------------------------------
    def _extract_amenity_entities(self, doc):
        text = doc.text
        spans = []

        for amenity in self.amenities:
            start = 0
            while True:
                idx = text.lower().find(amenity.lower(), start)
                if idx == -1:
                    break
                end = idx + len(amenity)
                span = doc.char_span(idx, end, label="AMENITY")
                if span is not None:
                    spans.append(span)
                start = end
        return spans
    
    def _extract_numeric_entities(self, doc):
        text = doc.text
        spans = []

        for pattern in self.bedroom_patterns:
            m = re.search(pattern, text, re.I)
            if m:
                span = doc.char_span(m.start(), m.end(), label="BEDROOMS")
                if span is not None:
                    spans.append(span)
                break

        for pattern in self.bathroom_patterns:
            m = re.search(pattern, text, re.I)
            if m:
                span = doc.char_span(m.start(), m.end(), label="BATHROOMS")
                if span is not None:
                    spans.append(span)
                break

        for pattern in self.price_patterns:
            m = re.search(pattern, text, re.I)
            if m:
                span = doc.char_span(m.start(), m.end(), label="PRICE")
                if span is not None:
                    spans.append(span)
                break

        for pattern in self.sqft_patterns:
            m = re.search(pattern, text, re.I)
            if m:
                span = doc.char_span(m.start(), m.end(), label="SQFT")
                if span is not None:
                    spans.append(span)
                break

        return spans

    def __call__(self, doc):
        final_spans = []
        final_spans.extend(self._extract_amenity_entities(doc))
        final_spans.extend(self._extract_numeric_entities(doc))

        # workaround because spaCy has its own NER entities that interfere with my spans
        # combined_spans = list(doc.ents) + final_spans
        combined_spans = final_spans

        # must filter out span overlaps with spaCy
        combined_spans = filter_spans(combined_spans)

       # then merge with existing entities
        doc.ents = combined_spans
        return doc

# ----------------------------------------------------------------------------
# Write to output labeled entity dataset file'
# ----------------------------------------------------------------------------
nlp = spacy.load("en_core_web_sm")
# nlp = spacy.load("en_core_web_sm", disable=["ner"]) # possibility if span problems persist
nlp = add_entity_extractor(nlp, "data/processed/taxonomy.json")
df = pd.read_csv("data/processed/listing_remarks.csv")

#def add_entity_extractor(nlp, taxonomy_path):
    #extractor = EntityExtractor(nlp, taxonomy_path)
    #nlp.add_pipe(extractor, name="entity_extractor", last=True)
    #return nlp

labeled_data = []
for remark in df["remarks"]:
    doc = nlp(remark)
    entities = []
    readable_entities = []

    for ent in doc.ents:
        start = ent.start_char
        end = ent.end_char
        label = ent.label_
        text_span = remark[start:end]

        # for spaCy training
        entities.append([start, end, label])

        # for human legibility
        readable_entities.append({
            "start": start,
            "end": end,
            "label": label,
            "span_text": text_span
        })
        
    labeled_data.append({
        "text": remark,
        # "entities": entities, # if I only want entries without readability
        "readable_entities": readable_entities
    })

output_path = "scripts/NER/labeled_entity_dataset.json"
with open(output_path, "w") as f:
    json.dump(labeled_data, f, indent=2)

print(f"Labeled dataset written to {output_path}")