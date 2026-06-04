"""
AI Agent service — the ReAct agent loop for ACME Customer Support.

This module wires together:
* The ``ChatGoogleGenerativeAI`` LLM (gemini-2.5-flash-lite, temp 0.4)
* The 3 agent tools (search_company_knowledge, lookup_order, create_refund_ticket)
* A buffer memory for short conversations (<10 messages)
* A comprehensive system prompt that defines the agent's persona

The agent uses a **ReAct** (Reason→Act→Observe) loop with a hard
``max_iterations=5`` guard rail to prevent runaway tool loops.
"""

import logging
import uuid
from typing import Dict, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

from config import get_settings
from services.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are **ACME Support Bot**, the friendly and professional AI customer \
support agent for **ACME Corporation** — a leading technology solutions \
provider founded in 2010.

━━━ YOUR PERSONA ━━━
• Warm, empathetic, and patient. Greet every customer with a friendly welcome.
• Professional but approachable — use clear, jargon-free language.
• You represent ACME Corporation and always act in the customer's best interest.

━━━ YOUR CAPABILITIES ━━━
You have access to the following tools:

1. **search_company_knowledge** — Search ACME's internal knowledge base for \
   information about policies, products, services, company history, security, \
   sustainability, and more.
2. **lookup_order** — Look up a specific order by its Order ID from the live \
   orders database.
3. **create_refund_ticket** — Create a refund/support ticket in the ticketing \
   system.

━━━ YOUR APPROACH: Listen → Analyse → Identify → Communicate → Verify ━━━

**Step 1 — Listen**: Read the customer's message carefully. Identify their \
intent (general inquiry, order status, refund request, complaint, etc.).

**Step 2 — Analyse**: Determine which tool(s) you need to call, if any. \
For simple greetings or chit-chat, respond directly without tools.

**Step 3 — Identify**: Gather all required information before acting:
  • For order lookups: ensure you have the Order ID.
  • For refund tickets: ensure ALL three pieces are confirmed:
    (a) Order ID — verified via lookup_order.
    (b) Customer name — confirmed against the order record.
    (c) Reason for refund — clearly stated by the customer.

**Step 4 — Communicate**: Provide a helpful, accurate response. Format \
information clearly. If the customer needs to take action, explain the steps.

**Step 5 — Verify**: Ask if there is anything else you can help with.

━━━ CRITICAL RULES ━━━
1. **NEVER fabricate** order details, ticket IDs, or any data. Only report \
   what the tools return.
2. If an order is **not found**, say so honestly and ask the customer to \
   verify the ID.
3. If you **don't know** the answer, admit it. Offer to connect the customer \
   with a human agent if needed.
4. **Before creating a refund ticket**, you MUST:
   (a) Look up the order using lookup_order to verify it exists.
   (b) Confirm the customer's name matches the order.
   (c) Collect the reason for the refund from the customer.
   NEVER skip any of these steps.
5. If the customer's request is **outside your capabilities**, politely \
   explain what you can help with and suggest alternatives.
6. Keep responses concise but complete — avoid unnecessary filler.
7. Use markdown formatting (bold, bullet points) for readability when listing \
   order details or multiple items.
8. Protect customer privacy — never repeat sensitive data unnecessarily.
"""

# ---------------------------------------------------------------------------
# Prompt template for the ReAct agent
# ---------------------------------------------------------------------------

REACT_PROMPT_TEMPLATE = """\
{system_prompt}

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}"""


# ---------------------------------------------------------------------------
# Conversation memory store  (keyed by conversation_id)
# ---------------------------------------------------------------------------
_memory_store: Dict[str, ConversationBufferMemory] = {}


def _get_memory(conversation_id: str) -> ConversationBufferMemory:
    """Get or create a buffer memory for the given conversation."""
    if conversation_id not in _memory_store:
        _memory_store[conversation_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=False,
            output_key="output",
        )
    return _memory_store[conversation_id]


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def _build_agent_executor(
    conversation_id: str,
) -> AgentExecutor:
    """Construct a fresh ``AgentExecutor`` with the ReAct agent.

    Args:
        conversation_id: Key for the conversation memory buffer.

    Returns:
        A configured ``AgentExecutor`` with ``max_iterations=5``.
    """
    settings = get_settings()

    llm = ChatGoogleGenerativeAI(
        model="gemma-4-26b-a4b-it",
        temperature=0.4,
        google_api_key=settings.google_api_key,
        convert_system_message_to_human=True,
    )

    prompt = ChatPromptTemplate.from_template(REACT_PROMPT_TEMPLATE)
    prompt = prompt.partial(system_prompt=SYSTEM_PROMPT)

    agent = create_react_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=prompt,
    )

    memory = _get_memory(conversation_id)

    executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )

    return executor


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def chat(message: str, conversation_id: Optional[str] = None) -> dict:
    """Process a customer message and return the agent's reply.

    This is the main entry point called by the API route.

    Args:
        message: The sanitised customer message.
        conversation_id: Optional conversation ID for memory continuity.
            A new UUID is generated if not provided.

    Returns:
        A dict with ``reply`` and ``conversation_id`` keys.
    """
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    logger.info(
        "Processing message [conv=%s]: %s",
        conversation_id,
        message[:80] + ("…" if len(message) > 80 else ""),
    )

    try:
        executor = _build_agent_executor(conversation_id)
        result = await executor.ainvoke({"input": message})
        reply = result.get("output", "I'm sorry, I wasn't able to generate a response. Please try again.")

        logger.info("Agent reply [conv=%s]: %s", conversation_id, reply[:120])
        return {"reply": reply, "conversation_id": conversation_id}

    except Exception as exc:
        logger.exception("Agent error [conv=%s]: %s", conversation_id, exc)
        return {
            "reply": (
                "I apologise, but I'm experiencing a temporary issue. "
                "Please try again in a moment, or contact our support team "
                "directly for immediate assistance."
            ),
            "conversation_id": conversation_id,
        }
