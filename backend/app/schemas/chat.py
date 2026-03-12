from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    question: str
    file_context: str
    conversation: List[ChatMessage] = []
    image_base64: Optional[str] = None
    rows: Optional[List[dict]] = None      # full dataset rows
    headers: Optional[List[str]] = None    # column names