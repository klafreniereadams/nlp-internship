# ComplianceChecker.py

# code scaffolding provided by IDX Exchange, and expanded with the 
# help of guided copilot prompting

# In the United States, certain rights and protections are granted
# to renters, borrowers, and buyers of housing. It is illegal to discrimitate
# against an individual seeking housing based on their race, religion, sex, 
# national origin, familial status, or disability.
# https://www.justice.gov/crt/fair-housing-act-1

# It is important that a product/app listing housing properties adhere
# to this Act for moral and legal reasons.

from difflib import SequenceMatcher

class ComplianceChecker:
    def __init__(self):
        self.prohibited_patterns = {
            'familial': [
                'children',
                'adults only',
                'adult living',
                'mature couple',
                'singles',
                'single professional',
                'not suitable for children',
                'dependents',
                'raising kids',
                'live alone',
                'for families with'
            ],
            'sex': [
                'woman',
                'man',
                'men',
                'women',
                'bachelor',
                'ladies',
                'singles'
            ],
            'sexual orientation': [
                'LGBT',
                'gay',
                'affirming',
                'traditional family',
                'straight couple'
            ],
            'disability': [
                'wheelchairs',
                'able-bodied',
                'not suitable for wheelchairs',
                'mentally'
            ],
            'race': [
                'white neighborhood',
                'ethnic',
                'African American',
                'Asian neighborhood',
                'diverse area',
                'restricted neighborhood',
            ],
            'religion': [
                'christian',
                'jewish',
                'muslim',
                'church',
                'buddhist',
                'spiritual',
                'chapel',
                'temple',
                'mosque',
                'churchgoers',
                'worshippers',
                'religious'
            ],
            'national_origin': [
                'Americans',
                'citizens',
                'immigrants',
                'visa',
                'hispanic',
                'latin',
                'latino'
            ]
        }

        # Indirect wording for fuzzy keyword matching
        self.category_keywords = {
            'familial': [
                'young kids',
                'kids',
                'children',
                'child-free',
                'adult-oriented',
                'adult focused',
                'adults',
                'family obligations',
                'family-friendly',
                'dependents',
                'family responsibilities',
                'noise',
                'better suited'
            ],
            'disability': [
                'mobility',
                'navigate stairs',
                'steep',
                'walkways',
                'accessibility',
                'assistive devices',
                'adaptive features'
                'wheelchair',
                'narrow hallways',
                'uneven flooring',
                'able-bodied',
                'special accommodations',
                'without assistance',
                'for residents with',
                'for people with'
            ],
            'race': [
                'traditional demographic',
                'population profile',
                'community makeup',
                'demographic',
                'cultural history',
                'heritage',
                'established background',
                'exclusive community'
            ],
            'religion': [
                'faith-centered',
                'religious',
                'faith',
                'worship',
                'spiritual identity,'
                'church'
            ],
            'national_origin': [
                'cultural background',
                'national heritage',
                'cultural identity',
                'national background',
                'cultural roots',
                'national makeup',
                'national traditions',
                'national identity'
            ]
        }

        self.context_modifiers = [
            'perfect for',
            'ideal for',
            'suited for'
        ]

    def fuzzy_match(self, keyword, text, threshold=0.65):
        words = text.split()
        score = 0.0

        for window_size in range(2, 5):  # 2–4 word windows
            for i in range(len(words) - window_size + 1):
                window = " ".join(words[i:i+window_size])
                ratio = SequenceMatcher(None, keyword, window).ratio()
                if ratio >= threshold:
                    score += 1.0
                elif ratio >= threshold - 0.10:
                    score += 0.5

        return score >= 1.5



    def check_listing(self, text):
        violations = []
        text_lower = text.lower()

        # exact pattern matching
        for category, patterns in self.prohibited_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    severity = 'error'

                    # context modifiers may precede 'commuting', 'entertaining', 'relaxing'
                    # but may not appear adjacent to an identity pattern without flagging
                    for modifier in self.context_modifiers:
                        if modifier in text_lower:
                            idx_mod = text_lower.find(modifier)
                            idx_pat = text_lower.find(pattern)
                            if abs(idx_mod - idx_pat) <= 6:
                                severity = 'warning'

                    violations.append({
                        'category': category,
                        'pattern': pattern,
                        'severity': severity,
                        'message': f'Prohibited language: {pattern} (Fair Housing Act violation)'
                    })

        # Fuzzy matching
        self.fuzzy_thresholds = {
        'familial': 0.60,
        'disability': 0.59,
        'race': 0.61,
        'religion': 0.63,
        'national_origin': 0.63
        # 0.65, 0.65, 0.75, 0.75, 0.78
}
        for category, keywords in self.category_keywords.items():
            for kw in keywords:
                kw_lower = kw.lower()

                if kw_lower in text_lower or self.fuzzy_match(
                    kw_lower,
                    text_lower,
                    threshold=self.fuzzy_thresholds[category]):
                        # Avoid duplicating exact pattern violations
                        already_flagged = any(v['category'] == category for v in violations)
                        if not already_flagged:
                            violations.append({
                                'category': category,
                                'pattern': kw,
                                'severity': 'warning',
                                'message': f'Potential prohibited language (keyword match): {kw} (Fair Housing risk)'
                            })

        return {'compliant': len(violations) == 0, 'violations': violations}


# The American Department of Housing and Urban Development maintains 
# a database of Fair Housing Act cases filed over a number of years regarding
# complaints of FHA violations. This could be a potential robust source
# of real training data for this ComplianceChecker.
# https://data.hud.gov/datasets.html