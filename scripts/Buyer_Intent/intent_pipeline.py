# intent_pipeline.py

# wrapper that integrates query_parser.py from Week 4 (SQL_Queries/)

# generated with copilot for direction and speed
from intent_classifier import IntentClassifier
from SQL_Queries.query_parser import QueryParser

class IntentPipeline:
    def __init__(self):
        self.intent_clf = IntentClassifier()
        self.parser = QueryParser()

    def process(self, user_query):
        # 1. Intent classification
        intent, confidence = self.intent_clf.predict(user_query)

        # 2. Query parsing
        filters = self.parser.parse(user_query)

        # 3. Combined output
        return {
            "query": user_query,
            "intent": intent,
            "confidence": float(confidence),
            "filters": filters
        }

# next use test_inference.py to see a few user queries in action #