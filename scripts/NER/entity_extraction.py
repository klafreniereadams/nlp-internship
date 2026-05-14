import re
import json
import spacy
from spacy.pipeline import EntityRuler
from text_cleaning import TextCleaner


class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm") # ? correct way to specify the spacy model?

    # should detect amenities identified during text_cleaning
    def extract_amenities(self, text):
        amenities = ['pool', 'gym', 'parking', 'doorman', 'elevator', 'balcony', 'fireplace', 'garage', 'natural light', 'stainless steel', 'spa', 'home office', 'formal dining room']
        found_amenities = []
        for amenity in amenities:
            if re.search(r'\b' + re.escape(amenity) + r'\b', text, re.I):
                found_amenities.append(amenity)
        return found_amenities

    def extract_bedrooms(self, text):
        patterns = [
            r'(\d+)\s*(?:bed|br|bedroom)s?',
            r'(\d+)bd'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        return None
    
    def extract_bathrooms(self, text):
        patterns = [
            r'(\d+(\.\d+)?)\s*(?:bath|ba|bathroom)s?',
            r'(\d+(\.\d+)?)\s*ba'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return float(match.group(1))
        return None

    def extract_price(self, text):
        # Assumes cleaned text from Week 2
        match = re.search(r'\$?(\d{5,})', text)
        return int(match.group(1)) if match else None
    
    def extract_sqft(self, text):
        match = re.search(r'(\d{3,})\s*(sq\s*\.?\s*ft|sqft|sq\.?ft\.?)', text, re.I)
        return int(match.group(1)) if match else None

    def extract_all(self, text):
        return {
            'bedrooms': self.extract_bedrooms(text),
            'bathrooms': self.extract_bathrooms(text),
            'price': self.extract_price(text),
            'sqft': self.extract_sqft(text),
            'amenities': self.extract_amenities(text)
        }

# create existing amenity taxonomy (found_amenities) based on the top n-grams found during text cleaning




# and match the taxonomy to where they occur in the listing remarks --> labeled dataset of listing remarks with the amenities labeled




# create a labeled dataset of 200-300 remarks. Manually mark the spans of each entity, put them in a JSON, CSV, or spaCy file. Use this to evaluate the Regex extraction performance.
# Optionally train a spaCy NER model

# short script for precision, recall, F1: Rum the extractor on the labeled dataset, compare the true entities to predicted entities. Calculate metrics. Achieve at least 85% F1. \

# Briefly explain any errors and propose improvements.



