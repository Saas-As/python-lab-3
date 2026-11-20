"""FastAPI приложение: веб-версия генератора цитат и фактов."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.data.seed import SEED_DATA
from app.models import CATEGORIES, KINDS
from web import crud
from web.database import Base, engine, get_db
from web.models import QuoteORM
from web.schemas import QuoteCreate, QuoteResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создаёт таблицы и заполняет БД стартовыми данными при старте."""
    Base.metadata.create_all(bind=engine)
    # Заполнение seed-данными (если БД пуста)
    from web.database import SessionLocal
    db = SessionLocal()
    try:
        count = db.query(QuoteORM).count()
        if count == 0:
            for seed in SEED_DATA:
                db.add(QuoteORM(
                    text=seed.text,
                    category=seed.category,
                    kind=seed.kind,
                    source=seed.source,
                ))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="Генератор цитат и фактов", lifespan=lifespan)

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------- HTML-страница ----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    items = crud.get_all(db)
    counts = crud.count_by_category(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "items": items,
            "categories": CATEGORIES,
            "kinds": KINDS,
            "counts": counts,
            "total": len(items),
            # Передаем данные для графика в формате JSON
            "chart_labels": list(CATEGORIES),
            "chart_values": [counts.get(cat, 0) for cat in CATEGORIES],
        },
    )


# ---------- JSON API ----------

@app.get("/api/quotes", response_model=list[QuoteResponse])
def api_list(db: Session = Depends(get_db)):
    return crud.get_all(db)


@app.post("/api/quotes", response_model=QuoteResponse, status_code=201)
def api_create(data: QuoteCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_quote(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/quotes/{item_id}", status_code=204)
def api_delete(item_id: int, db: Session = Depends(get_db)):
    if not crud.delete_quote(db, item_id):
        raise HTTPException(status_code=404, detail="Запись не найдена")


@app.get("/api/random", response_model=QuoteResponse)
def api_random(
    category: str | None = None,
    kind: str | None = None,
    db: Session = Depends(get_db),
):
    item = crud.get_random(db, category, kind)
    if not item:
        raise HTTPException(status_code=404, detail="Нет записей по фильтру")
    return item


@app.get("/api/stats")
def api_stats(db: Session = Depends(get_db)):
    return {"by_category": crud.count_by_category(db), "total": len(crud.get_all(db))}