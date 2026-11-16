import pytest
from pydantic import ValidationError
from app.schemas import RAGQuery
def test_valid_query():assert RAGQuery(query="What is the return policy?",top_k=3).top_k==3
def test_short_query_rejected():
    with pytest.raises(ValidationError):RAGQuery(query="x")
