# test_inference.py

# Generated with copilot
from intent_classifier import IntentClassifier

clf = IntentClassifier()

tests = [
    "looking around at homes in San Fran",
    "I want a 4 bedroom house under 600k in Fresno",
    "I'm ready to buy a place with a pool and no HOA",
    "just browsing listings near LA"
]

for q in tests:
    intent, confidence = clf.predict(q)
    print(f"Query: {q}")
    print(f"Intent: {intent}")
    print(f"Confidence: {confidence:.4f}")
    print()

"""
Results:

Query: looking around at homes in San Fran
Intent: browsing
Confidence: 0.6174

Query: I want a 4 bedroom house under 600k in Fresno
Intent: researching
Confidence: 0.8640

Query: I'm ready to buy a place with a pool and no HOA
Intent: researching
Confidence: 0.6451

Query: just browsing listings near LA
Intent: browsing
Confidence: 0.8180

Shows low confidence on queries 1 and 3, and mislabels 3 as
'researching' when I would actually call that 'ready-to-buy'.
"""
