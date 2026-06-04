"""
Pydantic schemas for request/response validation.

All user-facing API inputs and outputs are validated through these models
to enforce type safety, input sanitization, and consistent response shapes.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Incoming chat message from the frontend.

    Attributes:
        message: The user's message text (1-2000 chars, sanitized).
        conversation_id: Optional ID to maintain conversation continuity.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The customer's message to the support agent.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional conversation identifier for context continuity.",
    )

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, value: str) -> str:
        """Strip leading/trailing whitespace and reject dangerous patterns."""
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty or whitespace-only.")

        # Block common injection patterns (prompt injection, script tags)
        dangerous_patterns = [
            r"<script.*?>",
            r"javascript:",
            r"on\w+\s*=",
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Message contains disallowed content.")

        return value

    @field_validator("conversation_id")
    @classmethod
    def sanitize_conversation_id(cls, value: Optional[str]) -> Optional[str]:
        """Only allow alphanumeric characters, hyphens, and underscores."""
        if value is None:
            return value
        value = value.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError(
                "conversation_id must contain only alphanumeric characters, "
                "hyphens, or underscores."
            )
        return value


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class ChatResponse(BaseModel):
    """Outgoing response returned to the frontend.

    Attributes:
        reply: The agent's response text.
        conversation_id: Echoed conversation identifier.
        timestamp: Server-side UTC timestamp of the response.
    """

    reply: str = Field(
        ...,
        description="The AI agent's reply to the customer.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation identifier for continuity.",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the response was generated.",
    )


class HealthResponse(BaseModel):
    """Health-check endpoint response."""

    status: str = Field(default="healthy", description="Service health status.")
    version: str = Field(default="1.0.0", description="API version.")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Current server time (UTC).",
    )
