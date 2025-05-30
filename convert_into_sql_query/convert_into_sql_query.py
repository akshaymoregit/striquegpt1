import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import text
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain

# Load environment variables
load_dotenv()

# DB credentials from .env
user = os.getenv("POSTGRES_USER")
password = quote_plus(os.getenv("POSTGRES_PASSWORD"))
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DB")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Build connection string with multi-schema access
db_uri = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?options=-csearch_path=amazon_ads,meta,shopify,tiktok"

# Connect to DB with exposed tables
db = SQLDatabase.from_uri(
    db_uri,
    include_tables=["ads", "meta_ads", "order", "tiktok_ads"],
    sample_rows_in_table_info=2
)

# Initialize OpenAI model
llm = ChatOpenAI(model="gpt-4-0125-preview", api_key=openai_api_key)

# LangChain enforces these exact input vars: input, top_k, table_info
sql_prompt = PromptTemplate.from_template("""
You are a PostgreSQL SQL expert. Generate only a syntactically correct SQL query (no markdown, no explanations).

Given this table info:
{table_info}

User input: {input}

Return only the SQL query.
""")
sql_prompt.input_variables = ["input", "top_k", "table_info"]

# Build the SQL generation chain
sql_chain = create_sql_query_chain(llm=llm, db=db, prompt=sql_prompt)

# User's natural language question
user_input = {
    "input": "Show me top 5 campaigns with highest clicks from amazon ads.",
    "top_k": 5
}

# Generate SQL
sql_query = sql_chain.invoke(user_input)
print("🧠 Generated SQL:\n", sql_query)

# Execute the SQL and print the results
try:
    with db._engine.connect() as connection:
        result = connection.execute(text(sql_query))
        rows = result.fetchall()
        print("\n📊 Query Results:")
        for row in rows:
            print(dict(row))
except Exception as e:
    print("❌ Error executing SQL:", str(e))
