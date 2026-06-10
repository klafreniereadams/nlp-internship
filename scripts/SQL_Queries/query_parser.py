import json
import re

# code scaffolding provided by IDX Exchange
# injection-safe SQL practices following the guidelines at 
# https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

class QueryParser:
    def parse(self, query):
        filters = {}
        # Price patterns
        if match := re.search(r'under\s+\$?(\d+)([km]?)', query, re.I):
            filters['price_max'] = self._parse_number(match.group(1), match.group(2))
            
        # Bedroom patterns
        if match := re.search(r'(\d+)\+?\s*(?:bed|br)', query, re.I):
            filters['bedrooms_min' if '+' in match.group(0) else 'bedrooms'] = int(match.group(1))

        return filters
    
    def to_sql(self, filters):
        conditions = []
        params = []

        if 'price_max' in filters:
            conditions.append('L_SystemPrice <= %s')
            params.append(filters['price_max'])
        if 'bedrooms' in filters:
            conditions.append('L_Keyword2 = %s')
            params.append(filters['bedrooms'])

        where_clause = ' AND '.join(conditions)
        return f"SELECT * FROM rets_property WHERE {where_clause}", params
    
# ------------------------------------------------------------------------
# Validation before generating SQL
# ------------------------------------------------------------------------

class SchemaValidator:
    def __init__(self, schema_path='data/schema.json'):
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.valid_cities = self._load_valid_cities()

    def validate_query(self, filters):
        errors = []
        # Check city exists in database
        if 'city' in filters:
            if filters['city'] not in self.valid_cities:
                errors.append(f"City '{filters['city']}' not found in database")
        
        # Check price range
        if 'price_max' in filters:
            if filters['price_max'] < 100000 or filters['price_max'] > 1000000:
                errors.append(f"Price {filters['price_max']} outside typical range")

        # Check bedroom count
        if 'bedrooms' in filters:
            if filters['bedrooms'] < 1 or filters['bedrooms'] > 10:
                errors.append(f"Bedroom count {filters['bedrooms']} seems invalid")
        return len(errors) == 0, errors

# Usage:
parser = QueryParser()
validator = SchemaValidator()
filters = parser.parse("3 bed in Portland under 500k")
valid, errors = validator.validate_query(filters)
if not valid:
    print(f"Query validation errors: {errors}")
    # Return helpful message to user
else:
    sql, params = parser.to_sql(filters)