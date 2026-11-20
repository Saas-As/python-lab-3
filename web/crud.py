"""Операции с базой данных для веб-версии."""

import random
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from web.models import QuoteORM
from web.schemas import QuoteCreate


def create_quote(db: Session, data: QuoteCreate) -> QuoteORM:
    """Создаёт запись. Бросает ValueError при дубликате (ловим в main.py)."""
    existing = db.execute(
        select(QuoteORM).where(QuoteORM.text == data.text)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Запись уже существует: «{data.text[:40]}…»")

    item = QuoteORM(
        text=data.text.strip(),
        category=data.category,
        kind=data.kind,
        source=data.source.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_all(db: Session) -> list[QuoteORM]:
    return db.execute(select(QuoteORM).order_by(QuoteORM.id)).scalars().all()


def delete_quote(db: Session, item_id: int) -> bool:
    item = db.get(QuoteORM, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def get_random(
    db: Session, category: str | None = None, kind: str | None = None
) -> QuoteORM | None:
    stmt = select(QuoteORM)
    if category:
        stmt = stmt.where(QuoteORM.category == category)
    if kind:
        stmt = stmt.where(QuoteORM.kind == kind)
    stmt = stmt.order_by(func.random()).limit(1)
    return db.execute(stmt).scalar_one_or_none()


def count_by_category(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(QuoteORM.category, func.count()).group_by(QuoteORM.category)
    ).all()
    return {cat: cnt for cat, cnt in rows}