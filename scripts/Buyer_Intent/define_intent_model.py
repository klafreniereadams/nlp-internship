# define_intent_model.py

import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split

# TF-IDF (term frequency, inverse document frequency)
# vecorizer surfaces salient words that aren't common across all queries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

# loads Buyer_Intent/user_queries.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "user_queries.csv")
df = pd.read_csv(csv_path)

# set labels
X = df["query"]
y = df["intent"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Vectorizer (TF-IDF)
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    stop_words="english"
)

# Fit the vectorizer to the model
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Model
model = LogisticRegression(max_iter=200)
model.fit(X_train_vec, y_train)

# Evaluation
y_pred = model.predict(X_test_vec)
acc = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("Accuracy:", acc)
print("Confusion Matrix:")
print(cm)

# Save trained artifacts
vectorizer_path = os.path.join(BASE_DIR, "intent_vectorizer.pkl")
model_path = os.path.join(BASE_DIR, "intent_model.pkl")

# wb - w creates the file if missing, overwrites if already exists
with open(vectorizer_path, "wb") as f:
    pickle.dump(vectorizer, f)

with open(model_path, "wb") as f:
    pickle.dump(model, f)