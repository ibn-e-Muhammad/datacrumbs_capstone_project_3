"""
LangChain tool definitions for the ACME Customer Support Agent.

Exactly **3 tools** are exposed (per the ai-agents-architect guidelines):
1. ``search_company_knowledge`` — RAG retrieval from the FAISS vector store
2. ``lookup_order`` — live fetch from the Google Sheets Orders tab
3. ``create_refund_ticket`` — write a new row to the Google Sheets Tickets tab

Each tool has a **detailed** description with USE WHEN / DO NOT USE guidance
so the LLM can reliably decide which tool to call (HIGH severity anti-pattern
if descriptions are vague).

Tool errors are **surfaced** back to the agent with recovery hints — never
swallowed silently.
"""

import json
import logging
from typing import Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from services import rag_service, sheets_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool 1: RAG Knowledge Search
# ---------------------------------------------------------------------------

class SearchKnowledgeInput(BaseModel):
    query: str = Field(description="A natural-language question about ACME Corporation.")

@tool(args_schema=SearchKnowledgeInput)
def search_company_knowledge(query: str) -> str:
    """Search ACME Corporation's internal knowledge base for information about
    the company's policies, products, services, values, history, security
    practices, sustainability initiatives, employee benefits, and more.

    USE WHEN:
    - The customer asks about company policies, return/refund policies, or
      warranty terms.
    - The customer asks what products or services ACME offers.
    - The customer asks about ACME's history, mission, values, or leadership.
    - The customer asks about data security, compliance certifications, or
      privacy practices.
    - The customer asks general questions about ACME Corporation.

    DO NOT USE WHEN:
    - The customer is asking about a specific order (use ``lookup_order``
      instead).
    - The customer wants to create a refund ticket (use
      ``create_refund_ticket`` instead).
    - The question is unrelated to ACME Corporation.

    Args:
        query: A natural-language question about ACME Corporation.

    Returns:
        Relevant excerpts from the company knowledge base, or an error
        message with recovery hints if the search fails.
    """
    try:
        logger.info("search_company_knowledge called with query: %s", query)
        result = rag_service.search_knowledge(query)
        return result
    except RuntimeError as exc:
        error_msg = (
            f"Knowledge base error: {exc}. "
            "The vector store may not be initialised. "
            "Hint: inform the customer that internal systems are temporarily "
            "unavailable and suggest they try again shortly."
        )
        logger.error(error_msg)
        return error_msg
    except Exception as exc:
        error_msg = (
            f"Unexpected error searching knowledge base: {type(exc).__name__}: {exc}. "
            "Hint: apologise to the customer and let them know you are "
            "unable to retrieve that information right now."
        )
        logger.exception(error_msg)
        return error_msg


# ---------------------------------------------------------------------------
# Tool 2: Order Lookup
# ---------------------------------------------------------------------------

class LookupOrderInput(BaseModel):
    order_id: str = Field(description="The unique order identifier (e.g. 'ORD-001').")

@tool(args_schema=LookupOrderInput)
def lookup_order(order_id: str) -> str:
    """Look up a specific customer order by its Order ID from the live
    ACME orders database (Google Sheets).

    USE WHEN:
    - The customer provides an order ID (e.g. "ORD-001", "ORD-123") and
      wants to know its status, details, or amount.
    - The customer asks "Where is my order?" and has given an order ID.
    - You need to verify that an order exists before creating a refund
      ticket.

    DO NOT USE WHEN:
    - The customer has NOT provided an order ID yet — ask them for it first.
    - The customer is asking a general question about ACME products or
      policies (use ``search_company_knowledge`` instead).
    - The customer wants to create a refund (use ``create_refund_ticket``
      after verifying the order with this tool first).

    Args:
        order_id: The unique order identifier (e.g. "ORD-001").

    Returns:
        A JSON-formatted string with order details (order_id, customer,
        item, status, amount) if found, or an error message with recovery
        hints.
    """
    try:
        logger.info("lookup_order called with order_id: %s", order_id)
        result = sheets_service.lookup_order(order_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        error_msg = (
            f"Error looking up order '{order_id}': {type(exc).__name__}: {exc}. "
            "Hint: apologise to the customer and ask them to verify the "
            "order ID or try again later."
        )
        logger.exception(error_msg)
        return error_msg


# ---------------------------------------------------------------------------
# Tool 3: Create Refund Ticket
# ---------------------------------------------------------------------------

class CreateRefundTicketInput(BaseModel):
    order_id: str = Field(description="The verified order ID (e.g. 'ORD-001').")
    reason: str = Field(description="The customer-provided reason for requesting a refund.")

@tool(args_schema=CreateRefundTicketInput)
def create_refund_ticket(
    order_id: str,
    reason: str,
) -> str:
    """Create a refund/support ticket in the ACME ticketing system for a
    verified order.

    USE WHEN:
    - ALL of the following conditions are met:
      1. The customer has provided a valid order ID.
      2. The order has been verified using ``lookup_order`` and was found.
      3. The customer's name has been confirmed against the order record.
      4. The customer has clearly stated a reason for the refund.
    - Only then should you call this tool to create the ticket.

    DO NOT USE WHEN:
    - The order ID has NOT been verified yet — use ``lookup_order`` first.
    - The customer has NOT confirmed their name yet — ask for confirmation.
    - The customer has NOT provided a reason for the refund — ask for one.
    - Any required information (order ID, customer name, reason) is missing.

    Args:
        order_id: The verified order ID (e.g. "ORD-001").
        reason: The customer-provided reason for requesting a refund.

    Returns:
        A JSON-formatted string with the new ticket details (ticket_id,
        order_id, reason, created_at) on success, or an error message
        with recovery hints.
    """
    try:
        logger.info(
            "create_refund_ticket called — order_id: %s, reason: %s",
            order_id,
            reason,
        )
        result = sheets_service.create_ticket(
            order_id=order_id,
            reason=reason,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        error_msg = (
            f"Error creating refund ticket for order '{order_id}': "
            f"{type(exc).__name__}: {exc}. "
            "Hint: apologise to the customer and let them know the ticket "
            "could not be created at this time. Suggest trying again shortly."
        )
        logger.exception(error_msg)
        return error_msg


# ---------------------------------------------------------------------------
# Tool registry (convenience list for the agent)
# ---------------------------------------------------------------------------

ALL_TOOLS = [
    search_company_knowledge,
    lookup_order,
    create_refund_ticket,
]
