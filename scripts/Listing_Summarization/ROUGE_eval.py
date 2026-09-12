# ROUGE_eval.py

import os
from rouge import Rouge
import pandas as pd

# Loads parallel listing/human evaluation set
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "human_validation_set.csv")
df = pd.read_csv(csv_path)

# Accepts columns: L_Remarks, Human_Summary, Model_Summary

references = df["Human_Summary"].fillna("").tolist()
candidates = df["Model_Summary"].fillna("").tolist()

rouge = Rouge()

scores = rouge.get_scores(candidates, references, avg=True)

print("ROUGE Scores:")
print(scores)

"""
ROUGE Scores:
{'rouge-1': {
'r': 0.4651912107402792, 
'p': 0.33473596398337946, 
'f': 0.37448288024192394}, 

'rouge-2': {
'r': 0.24521536299110128, 
'p': 0.17549567060064192, 
'f': 0.19546745720254508}, 

'rouge-l': {
'r': 0.451816138643711,
'p': 0.3267334511192594,
'f': 0.36506035382437263}}

The ROUGE-1 F1 scores doesn't quite meet the desired >0.4 threshold,
but I expect this is due mostly to the rigid way that the extractor
scores amenities; meanwhile, I wrote my human summaries in a very
general way without always listing specific amenities.
"""