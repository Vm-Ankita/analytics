from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    """
    Represents one message in a conversation.
    """

    role: str
    content: str


class AskRequest(BaseModel):
    """
    Request payload for /api/ask endpoint.

    Contains the user question, dataset context,
    and optional conversation history.
    """

    question: str
    file_context: str

    # Conversation history (previous chat messages)
    conversation: List[ChatMessage] = Field(default_factory=list)

    # Base64 image for vision models
    image_base64: Optional[str] = None

    # Dataset rows (for question answering)
    rows: Optional[List[Dict[str, Any]]] = None

    # Column headers
    headers: Optional[List[str]] = None