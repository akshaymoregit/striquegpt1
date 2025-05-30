import streamlit as st
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up the Streamlit app
st.set_page_config(page_title="Strique GPT", page_icon="🤖")

# Sidebar with chat history heading
with st.sidebar:
    st.header("Chat History")

# Main content area
st.title("🤖 Strique GPT V1")
st.markdown("Select a schema to view its tables, or enter a question to generate an SQL query.")

# Function to fetch schema details
def fetch_schema_details(schema_name):
    try:
        # Get DB credentials
        user = os.getenv("POSTGRES_USER")
        password = quote_plus(os.getenv("POSTGRES_PASSWORD"))
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        dbname = os.getenv("POSTGRES_DB")

        if not all([user, password, host, port, dbname]):
            return "Error: Missing database credentials in .env file."

        # Connection string
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        # Initialize engine
        engine = create_engine(connection_string)

        # Query to get tables for the specified schema
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema_name
        AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_name;
        """

        # Run query and fetch results
        with engine.connect() as connection:
            result = connection.execute(text(query), {"schema_name": schema_name})
            tables = result.fetchall()

        # Format the result
        if not tables:
            return f"No tables found in schema '{schema_name}'."
        
        table_list = [table[0] for table in tables]
        return f"📂 Schema: {schema_name}\n" + "\n".join([f"{i+1}. {table}" for i, table in enumerate(table_list)])
    except Exception as e:
        return f"Error fetching schema details: {str(e)}"

# List of available schemas
available_schemas = [
    "amazon_ads",
    "amazon_seller",
    "google_ads",
    "google_analytics",
    "meta",
    "shopify",
    "tiktok"
]

# Chat history container
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Schema selection dropdown and submission
with st.form(key="schema_form"):
    selected_schema = st.selectbox("Select a schema:", options=available_schemas, index=0)
    submit_button = st.form_submit_button("Fetch Schema")

# Process the schema selection
if submit_button:
    # Add user action to history
    st.session_state.messages.append({"role": "user", "content": f"Selected schema: {selected_schema}"})

    # Display user action
    with st.chat_message("user"):
        st.markdown(f"Selected schema: {selected_schema}")

    # Fetch and display schema details
    with st.spinner("Fetching schema details..."):
        result = fetch_schema_details(selected_schema)
        st.session_state.messages.append({"role": "assistant", "content": result})

        with st.chat_message("assistant"):
            st.markdown(result)

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()