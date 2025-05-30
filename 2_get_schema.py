import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

# Load .env for POSTGRES_URL
load_dotenv()
db_url = os.getenv("POSTGRES_URL")

# Create the DB engine
engine = create_engine(db_url)

# Query to fetch all available schemas
query = """
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema_name;
"""

# Execute and display the result
with engine.connect() as connection:
    result = connection.execute(text(query))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

print("📁 Available Schemas:")
print(df)
