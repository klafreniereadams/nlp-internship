import os
import pandas as pd
from ComplianceChecker import ComplianceChecker

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "violation_test_set.csv")

def evaluate_violations():
    df = pd.read_csv(csv_path)
    checker = ComplianceChecker()

    true_positives = 0
    false_positives = 0
    false_negatives = 0

    detailed_results = []

    for _, row in df.iterrows():
        listing_text = row["text"]
        expected = row["expected_violation"]

        result = checker.check_listing(listing_text)
        violations = result["violations"]

        detected_categories = {v["category"] for v in violations}

        if expected in detected_categories:
            true_positives += 1
        else:
            false_negatives += 1

        for cat in detected_categories:
            if cat != expected:
                false_positives += 1

        detailed_results.append({
            "id": row["id"],
            "text": listing_text,
            "expected": expected,
            "detected": list(detected_categories)
        })

    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0

    print("Recall:", recall)
    print("Precision:", precision)
    print("True Positives:", true_positives)
    print("False Positives:", false_positives)
    print("False Negatives:", false_negatives)

    return detailed_results

if __name__ == "__main__":
    evaluate_violations()

"""
Recall: 0.89
Precision: 0.478494623655914
True Positives: 178
False Positives: 194
False Negatives: 22

These were the best results I could achieve with exact and fuzzy 
content filtering.
"""