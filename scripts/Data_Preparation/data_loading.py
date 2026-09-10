import os
import mysql.connector
import pandas as pd
from scripts.Data_Preparation.text_cleaning import TextCleaner

os.makedirs('data/processed', exist_ok=True)

conn = mysql.connector.connect(
host='localhost', user='root', password='root', database='real_estate')
query ="""
SELECT L_ListingID, L_Address, L_City, L_Keyword2 as beds,
LM_Dec_3 as baths, L_SystemPrice as price, L_Remarks as remarks
FROM rets_property
WHERE L_Remarks IS NOT NULL AND LENGTH(L_Remarks) > 50
ORDER BY RAND() LIMIT 1000
"""

df = pd.read_sql(query, conn)
#df = df[df['remarks'].str.len() > 50].copy()
cleaner = TextCleaner()
df['price'] = df['price'].astype(str).apply(cleaner.normalize_prices)
df.to_csv('data/processed/listing_remarks.csv', index=False)
conn.close()


# writing cleaner = TextCleaner 
## Looks up the class TextCleaner (must already be imported above)
##Creates an instance of that class
## the instance now has access to all methods defined with self, including normalize_prices
# Assigns it to the variable cleaner  
# now you can call cleaner.normalize_prices("1.5k")