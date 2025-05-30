import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, load_prompt
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os
import json

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
st.markdown("Enter a question, and I'll classify it as a database-related question or a general question.")

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("Error: OPENAI_API_KEY not found. Please set it in your .env file.")
    st.stop()

# Initialize the model
try:
    model = ChatOpenAI(model="gpt-4o", temperature=0.0)
except Exception as e:
    st.error(f"Error initializing model: {str(e)}")
    st.stop()

# Load prompt template
try:
    template = load_prompt("template.json")
except FileNotFoundError:
    st.error("Error: template.json not found. Please ensure the file exists in the project directory.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error: Invalid JSON in template.json. Please check the file format.")
    st.stop()

# Create the LangChain chain for classification
def create_classification_chain():
    # Use JsonOutputParser to parse the LLM's output
    parser = JsonOutputParser()

    # Create the chain: Prompt -> LLM -> Parser
    chain = (
        {"input": RunnablePassthrough()}  # Pass the input directly
        | template
        | model
        | parser
    )
    return chain

# Initialize the chain
try:
    classification_chain = create_classification_chain()
except Exception as e:
    st.error(f"Error creating classification chain: {str(e)}")
    st.stop()

# Chat history container
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Input box in natural position
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("Enter your question:", key="user_input", placeholder="Type your question here...")
    submit_button = st.form_submit_button("Classify")

# Process the input when the form is submitted
if submit_button and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Classify the question
    with st.spinner("Classifying..."):
        try:
            result = classification_chain.invoke(user_input)
            # Extract the classification type
            question_type = result.get("type", "unknown")
            if question_type == "database":
                response = "Database-related question"
            elif question_type == "general":
                response = "General question"
            else:
                response = "Unable to classify the question"

            # Add classification result to history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Display classification result
            with st.chat_message("assistant"):
                st.markdown(response)
        except Exception as e:
            st.error(f"Error classifying question: {str(e)}")

# Show warning if input is empty
if submit_button and not user_input.strip():
    st.warning("Please enter a question before classifying.")

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()