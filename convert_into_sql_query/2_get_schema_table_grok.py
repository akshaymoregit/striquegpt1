import streamlit as st
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Initialize session state for chat history and schema tables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "schema_tables" not in st.session_state:
    st.session_state.schema_tables = []
if "selected_schema" not in st.session_state:
    st.session_state.selected_schema = None

# Set up the Streamlit app
st.set_page_config(page_title="Strique GPT", page_icon="🤖")

# Sidebar with chat history heading
with st.sidebar:
    st.header("Chat History")

# Main content area
st.title("🤖 Strique GPT V1")
st.markdown("Select a schema to view its tables, then select a table to view its columns.")

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
            return "Error: Missing database credentials in .env file.", []

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
            return f"No tables found in schema '{schema_name}'.", []
        
        table_list = [table[0] for table in tables]
        formatted_output = f"📂 Schema: {schema_name}\n" + "\n".join([f"{i+1}. {table}" for i, table in enumerate(table_list)])
        return formatted_output, table_list
    except Exception as e:
        return f"Error fetching schema details: {str(e)}", []

# Function to fetch column names for a table
def fetch_column_names(schema_name, table_name):
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

        # Query to get columns for the specified table
        query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = :schema_name
        AND table_name = :table_name
        ORDER BY column_name;
        """

        # Run query and fetch results
        with engine.connect() as connection:
            result = connection.execute(text(query), {"schema_name": schema_name, "table_name": table_name})
            columns = result.fetchall()

        # Format the result
        if not columns:
            return f"No columns found in table '{table_name}' in schema '{schema_name}'."
        
        column_list = [column[0] for column in columns]
        return f"📋 Columns for table '{table_name}' in schema '{schema_name}':\n" + "\n".join([f"{i+1}. {column}" for i, column in enumerate(column_list)])
    except Exception as e:
        return f"Error fetching column names: {str(e)}"

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
    # Store the selected schema
    st.session_state.selected_schema = selected_schema

    # Add user action to history
    st.session_state.messages.append({"role": "user", "content": f"Selected schema: {selected_schema}"})

    # Display user action
    with st.chat_message("user"):
        st.markdown(f"Selected schema: {selected_schema}")

    # Fetch and display schema details
    with st.spinner("Fetching schema details..."):
        result, table_list = fetch_schema_details(selected_schema)
        st.session_state.messages.append({"role": "assistant", "content": result})
        st.session_state.schema_tables = table_list

        with st.chat_message("assistant"):
            st.markdown(result)

# Table selection dropdown and submission (only show if tables are available)
if st.session_state.schema_tables:
    with st.form(key="table_form"):
        selected_table = st.selectbox(
            f"Select a table from '{st.session_state.selected_schema}':",
            options=st.session_state.schema_tables,
            index=0
        )
        table_submit_button = st.form_submit_button("Fetch Columns")

    # Process the table selection
    if table_submit_button:
        # Add user action to history
        st.session_state.messages.append({"role": "user", "content": f"Selected table: {selected_table}"})

        # Display user action
        with st.chat_message("user"):
            st.markdown(f"Selected table: {selected_table}")

        # Fetch and display column names
        with st.spinner("Fetching column names..."):
            result = fetch_column_names(st.session_state.selected_schema, selected_table)
            st.session_state.messages.append({"role": "assistant", "content": result})

            with st.chat_message("assistant"):
                st.markdown(result)

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.schema_tables = []
    st.session_state.selected_schema = None
    st.rerun()