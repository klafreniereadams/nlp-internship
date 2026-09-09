# intent_classifier.py
# runs pickle of define_intent_model.py

import os
import pickle

class IntentClassifier:
    def __init__(self):
        # dynamic path file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        vectorizer_path = os.path.join(BASE_DIR, "intent_vectorizer.pkl")
        model_path = os.path.join(BASE_DIR, "intent_model.pkl")
        # Loads TF-IDF vectorizer
        with open(vectorizer_path, "rb") as f:
            self.vectorizer = pickle.load(f)

        # Loads trained model
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        # Defines label order from csv of potential user queries
        self.labels = ['browsing', 'researching', 'ready_to_buy']

    # model inference
    def predict(self, query):
        X = self.vectorizer.transform([query])
        probas = self.model.predict_proba(X)[0]
        intent = self.labels[probas.argmax()]
        confidence = probas.max()
        return intent, confidence
