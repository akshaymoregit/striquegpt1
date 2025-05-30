import streamlit as st
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# DB credentials
user = os.getenv("POSTGRES_USER")
password = quote_plus(os.getenv("POSTGRES_PASSWORD"))
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DB")

# Create engine
connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
engine = create_engine(connection_string)

# List of relevant schemas
valid_schemas = [
    "amazon_ads", "amazon_seller", "google_ads",
    "google_analytics", "meta", "shopify", "tiktok"
]

# Streamlit UI
st.title("🔍 Select a Schema")
selected_schema = st.selectbox("Choose a schema:", valid_schemas)

if st.button("Fetch Tables"):
    # Query to get tables for the selected schema
    query = f"""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = '{selected_schema}';
    """

    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=["table_name"])
        
        if not df.empty:
            st.success(f"📂 Tables under schema: `{selected_schema}`")
            st.dataframe(df)
        else:
            st.warning("No tables found under this schema.")
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
