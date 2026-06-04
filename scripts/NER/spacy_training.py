# generated with Copilot's help

import json
from sklearn.metrics import precision_recall_fscore_support

# ---------------------------------------------------------
# Load gold labels (human‑corrected)
# ---------------------------------------------------------
with open("scripts/NER/gold_corrected.json") as f:
    gold_data = json.load(f)

gold_texts = [d["text"] for d in gold_data]
gold_entities = [d["entities"] for d in gold_data]

# ---------------------------------------------------------
# Load predicted labels
# ---------------------------------------------------------
with open("scripts/NER/labeled_entity_dataset.json") as f:
    pred_data = json.load(f)
    pred_data = pred_data[:len(gold_data)]

pred_entities = [d["readable_entities"] for d in pred_data]

# ---------------------------------------------------------
# Align gold and predicted datasets
# ---------------------------------------------------------
if len(gold_entities) != len(pred_entities):
    raise ValueError(
        f"Gold docs ({len(gold_entities)}) and predicted docs ({len(pred_entities)}) "
        "must have the same length."
    )
# ---------------------------------------------------------
# Convert spans → exact‑match tuples
# ---------------------------------------------------------
# Convert spans → exact‑match tuples
def span_key(e):
    return (e["start"], e["end"], e["label"])

gold_flat = []
pred_flat = []

for gold_doc, pred_doc in zip(gold_entities, pred_entities):
    pred_doc = pred_doc or []
    gold_flat.extend([span_key(e) for e in gold_doc])
    pred_flat.extend([span_key(e) for e in pred_doc])

gold_set = set(gold_flat)
pred_set = set(pred_flat)

tp = len(gold_set & pred_set)
fp = len(pred_set - gold_set)
fn = len(gold_set - pred_set)

precision = tp / (tp + fp) if tp + fp > 0 else 0
recall = tp / (tp + fn) if tp + fn > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0

print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

# Precision: 0.6897311591009255
# Recall: 0.73751178133836
# F1 Score: 0.7128216807105443

# these eval scores do not meet the desired threshold of 
# >0.8, but I'm realizing the complexity of all the 
# ways realtors abbreviate bedrooms, bathrooms, and 
# square footage. Going back and building out a quite
# robust set of regex rules to account for all of this will
# almost certainly boost my eval scores


