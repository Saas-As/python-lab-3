"""Pydantic-схемы для валидации запросов и ответов."""

from datetime import datetime
from pydantic import BaseModel, Field

from app.models import CATEGORIES, KINDS


class QuoteCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    category: str = Field(..., description=f"Одна из: {', '.join(CATEGORIES)}")
    kind: str = Field(default="Цитата", description=f"Одна из: {', '.join(KINDS)}")
    source: str = Field(default="", max_length=100)


class QuoteResponse(BaseModel):
    id: int
    text: str
    category: str
    kind: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True  # позволяет читать из ORM-объектов