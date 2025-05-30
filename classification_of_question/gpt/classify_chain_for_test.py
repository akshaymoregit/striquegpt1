from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableMap

response_schemas = [
    ResponseSchema(name="type", description="The type of question, either 'general' or 'database'")
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

classification_prompt = PromptTemplate(
    template="""You are an AI assistant. Classify the user's question as either a general question or a database-related question.

Question: {question}

Return the result in this format:
{format_instructions}
""",
    input_variables=["question"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

classification_chain = classification_prompt | llm | output_parser
