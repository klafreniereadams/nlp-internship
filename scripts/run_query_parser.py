import mysql.connector
from scripts.SQL_Queries.query_parser import QueryParser, SchemaValidator

# Connect to DB
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='real_estate'
)

# Create parser + validator
parser = QueryParser()
validator = SchemaValidator(db_conn=conn)

# Parse a query
filters = parser.parse("3 bed in Portland under 500k")

# Validate
valid, errors = validator.validate_query(filters)

if valid:
    sql, params = parser.to_sql(filters)
    print(sql)
    print(params)
else:
    print("Errors:", errors)

conn.close()