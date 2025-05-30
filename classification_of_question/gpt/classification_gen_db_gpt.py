from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableMap
import streamlit as st

# Define response schema
response_schemas = [
    ResponseSchema(name="type", description="The type of question, either 'general' or 'database'")
]

# Create output parser
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# Define prompt template
classification_prompt = PromptTemplate(
    template="""You are an AI assistant. Classify the user's question as either a general question or a database-related question.

Question: {question}

Return the result in this format:
{format_instructions}
""",
    input_variables=["question"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
)

# Define the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Create the classification chain
classification_chain = classification_prompt | llm | output_parser

# Streamlit UI
st.set_page_config(page_title="Question Classifier", layout="centered")
st.title("🧠 Strique Question Classifier")

# Input from user
user_input = st.text_input("Enter your question to classify:")

if st.button("Classify"):
    if user_input.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Classifying..."):
            try:
                result = classification_chain.invoke({"question": user_input})
                q_type = result["type"]
                st.success(f"This is a **{q_type.upper()}** question.")
            except Exception as e:
                st.error(f"Error: {e}")
