# Генератор цитат и фактов с выбором тематики

Приложение для хранения, просмотра и генерации цитат и интересных фактов по выбранной тематике.
Реализовано в двух вариантах: **десктопное приложение** (PySide6) и **веб-версия** (FastAPI + PostgreSQL).

**Вариант 10.** Сложность: **Well-done** (Rare + Medium + Well-done).

---

## Возможности

- Просмотр списка всех цитат и фактов в виде таблицы.
- Добавление новых записей с выбором тематики, типа (цитата/факт) и указанием источника.
- Удаление записей.
- **Генератор случайных цитат/фактов** с фильтрацией по тематике и типу.
- **График активности** (распределение записей по тематикам).
- **Лог активности** (история действий пользователя).
- Меню «Файл → Выход» и «Справка → О программе» (в десктопной версии).
- Обработка ошибок с помощью собственных исключений.

**Доступные тематики:** Наука, Мотивация, История, Юмор, Философия, Факты о мире.
**Типы записей:** Цитата, Факт.

---

## Десктопная версия (PySide6)

### Требования
- Python 3.10+
- ОС: Windows / Linux / macOS

### Запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ВАШ_ЛОГИН/quote-fact-generator.git
   cd quote-fact-generator
   ```

2. **Создайте и активируйте виртуальное окружение:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите приложение:**
   ```bash
   python main.py
   ```

*(При первом запуске автоматически создастся локальная база данных SQLite `quotes.db` и заполнится стартовыми данными).*

---

## Веб-версия (FastAPI + PostgreSQL + Docker)

### Требования
- Docker Desktop (или Docker Engine + Docker Compose)

### Запуск

1. **Соберите и запустите контейнеры:**
   ```bash
   docker compose up --build -d
   ```

2. **Дождитесь запуска** (около 10–15 секунд). Проверьте статус:
   ```bash
   docker compose ps
   ```
   Оба контейнера (`quotes-db` и `quotes-web`) должны быть в статусе `Up`.

3. **Откройте приложение в браузере:**
   - **Веб-интерфейс:** http://localhost:8000
   - **Документация API (Swagger):** http://localhost:8000/docs

### Остановка

```bash
docker compose down
```

*(Чтобы удалить базу данных вместе с контейнерами, используйте `docker compose down -v`).*

### API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/quotes` | Список всех записей |
| `POST` | `/api/quotes` | Создать новую запись |
| `DELETE` | `/api/quotes/{id}` | Удалить запись по ID |
| `GET` | `/api/random` | Случайная запись (фильтры: `?category=Наука&kind=Факт`) |
| `GET` | `/api/stats` | Статистика по категориям |

---

## Структура проекта

```text
quote-fact-generator/
│
├── app/                      # Десктопная версия (PySide6)
│   ├── models.py             # Модели данных (Quote)
│   ├── exceptions.py         # Собственные исключения
│   ├── repository.py         # Работа с БД (SQLite)
│   ├── data/seed.py          # Стартовые данные
│   └── gui/                  # Виджеты Qt (таблица, график, лог, окно)
│
├── web/                      # Веб-версия (FastAPI)
│   ├── main.py               # Точка входа, роуты
│   ├── database.py           # Подключение к PostgreSQL (SQLAlchemy)
│   ├── models.py             # ORM-модели
│   ├── schemas.py            # Pydantic-схемы
│   ├── crud.py               # CRUD-операции
│   └── templates/index.html  # HTML-интерфейс (Jinja2 + Chart.js)
│
├── tests/                    # Тесты (pytest)
│   ├── test_models.py
│   └── test_repository.py
│
├── main.py                   # Запуск десктопного приложения
├── requirements.txt          # Зависимости для десктопа
├── requirements-web.txt      # Зависимости для веб-версии
├── docker-compose.yml        # Конфигурация Docker (FastAPI + PostgreSQL)
├── Dockerfile                # Сборка веб-образа
└── README.md
```

---

## Технологии

- **Язык:** Python 3.12
- **GUI:** PySide6 (Qt for Python)
- **Веб-фреймворк:** FastAPI
- **Базы данных:** SQLite (десктоп), PostgreSQL (веб-версия)
- **ORM:** SQLAlchemy 2.0
- **Валидация:** Pydantic
- **Шаблонизатор:** Jinja2
- **Графики:** QtCharts (десктоп), Chart.js (веб)
- **Тестирование:** pytest
- **Контейнеризация:** Docker, Docker Compose

---

## Тестирование

Тесты покрывают логику валидации моделей и работу репозитория.

**Запуск тестов (для десктопной версии):**
```bash
pytest tests/ -v
```

Ожидаемый результат: **9 passed**.

---

## Обработка ошибок

Приложение использует собственные исключения (наследники `AppError`):
- `EmptyTextError` — пустой текст;
- `TextTooLongError` — превышение лимита символов;
- `InvalidCategoryError` / `InvalidKindError` — недопустимые значения;
- `DuplicateItemError` — попытка добавить дубликат;
- `ItemNotFoundError` — запись не найдена;
- `NoQuotesInCategoryError` — нет записей для выбранного фильтра.

---