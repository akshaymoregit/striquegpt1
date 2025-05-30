import pytest
from classify_chain_for_test import classification_chain

@pytest.mark.parametrize("question,expected_type", [
    ("What is the capital of France?", "general"),
    ("How many rows are in the users table?", "database"),
    ("List all columns in the sales database", "database"),
    ("Who is the Prime Minister of India?", "general")
])
def test_question_classification(question, expected_type):
    result = classification_chain.invoke({"question": question})
    assert "type" in result, "Missing 'type' in result"
    assert result["type"].lower() == expected_type, f"Expected {expected_type}, got {result['type']}"
