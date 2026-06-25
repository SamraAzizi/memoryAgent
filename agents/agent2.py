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
@tool(approval_required=True)
def process_refund(order_id: str, amount: float) -> str:
    """request a refund, pause for human approvla think before you run this"""
    return f"Refunded {amount:.2f} for order {order_id}"


@guardrail
def safe_support_request(prompt: str) -> GuardrailResult:
    """Block obvious prompt injection attempts"""
    blocked = ["ignore", "ignore previous", "system prompt", "jailbreak"]
    passed = not any(phrase in prompt.lower() for phrase in blocked)
    return GuardrailResult(passed=passed, message="Please ask a normal question, this is blocked.")


support_agent = Agent(
    name="support_agent",
    model="openai/gpt-5.4",
    instructions=(
        "You are a customer support agent. Use the knowledge base first. "
        "If the customer wants a refund: when you know the order ID, call "
        "lookup_order to get the amount. Before calling process_refund, "
        "write a short plain-English sentence describing exactly what refund "
        "you are about to issue, for example: 'I am going to refund $49.99 "
        "for order A100.' Then call process_refund. The tool will pause for "
        "human approval automatically. If the order ID is missing, ask the "
        "customer for it. Always populate the message field with a clear reply."
    ),
    output_type=SupportResponse,
    tools=[search_knowledge_base, lookup_order, process_refund],
    memory=ConversationMemory(max_messages=50),
    guardrails=[Guardrail(safe_support_request, position=Position.INPUT, on_fail=OnFail.RAISE)],
    max_turns=10
)