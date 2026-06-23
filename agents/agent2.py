import logging

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agentspan.agents import (
    Agent,
    AgentRuntime,
    ConversationMemory,
    EventType,
    Guardrail,
    GuardrailResult,
    OnFail,
    Position,
    guardrail,
    start,
    tool,
)


load_dotenv(override=True)
logging.basicConfig(level=logging.WARNING, force=True)
logging.disable(logging.INFO)


MOCK_DB = {
    "orders": {"A100": {"status": "delivered", "total": 49.99}},
    "accounts": {"tim@example.com": {"status": "active", "tier": "pro"}},
}

DOCS = {
    "refund policy": "Refunds are processed within 5 business days.",
    "shipping": "Standard shipping takes 3 to 7 business days.",
    "account": "Pro accounts include priority support.",
}

class SupportRespoinse(BaseModel):
    stage: str = Field(description="The stage of the support process, e.g., 'initial', 'follow-up', 'resolution'.")
    successful:bool
    message: str

@tool
def search_knowledge_base(query: str) -> str:
    """search support docs"""
    for title,body in DOCS.items():
        if title in query.lower():
            return body
    return "No matching support article found"

@tool
def lookup_order(order_id: str) -> dict:
    """lookup order in database by ID"""
    return MOCK_DB["orders"].get(order_id, {"error": "Order not found"})