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

# Valid schemas
valid_schemas = [
    "amazon_ads", "amazon_seller", "google_ads",
    "google_analytics", "meta", "shopify", "tiktok"
]

# Session state setup
if "tables" not in st.session_state:
    st.session_state.tables = []
if "selected_schema" not in st.session_state:
    st.session_state.selected_schema = None

st.title("🧠 Database Schema Explorer")

# 1️⃣ Select Schema
selected_schema = st.selectbox("Step 1: Choose a schema", valid_schemas)

if st.button("🔍 Fetch Tables"):
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
            st.success(f"Found {len(df)} tables in `{selected_schema}`")
            st.dataframe(df)
            st.session_state.tables = df['table_name'].tolist()
            st.session_state.selected_schema = selected_schema
        else:
            st.warning("No tables found.")
    except Exception as e:
        st.error(f"Error: {e}")

# 2️⃣ Only show table select if tables were fetched
if st.session_state.tables and st.session_state.selected_schema:
    selected_table = st.selectbox("Step 2: Choose a table", st.session_state.tables)

    if st.button("📊 Show Columns"):
        query_columns = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = '{st.session_state.selected_schema}' 
              AND table_name = '{selected_table}';
        """
        try:
            with engine.connect() as connection:
                result = connection.execute(text(query_columns))
                cols_df = pd.DataFrame(result.fetchall(), columns=["Column Name", "Data Type"])
            if not cols_df.empty:
                st.success(f"📋 Columns in `{selected_table}`:")
                st.dataframe(cols_df)
            else:
                st.warning("No columns found.")
        except Exception as e:
            st.error(f"Error fetching columns: {e}")
