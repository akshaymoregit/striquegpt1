import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

# Load .env file
load_dotenv()

# Read connection URL
db_url = os.getenv("POSTGRES_URL")

# Initialize engine
engine = create_engine(db_url)

# Run test query
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');"))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    print(df)
