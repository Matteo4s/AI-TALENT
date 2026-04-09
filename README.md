# AI Talent (FastAPI + PostgreSQL + Next.js)

Система для поиска перспективных кандидатов на GitHub:
- backend на FastAPI;
- база PostgreSQL для сохранения кандидатов;
- frontend на Next.js с цветовой шкалой перспективности.

## Что реализовано

- Поиск кандидатов через GitHub API.
- Сохранение кандидатов в PostgreSQL (таблица `candidates`).
- Фильтры:
  - исключение компаний (`exclude_companies`);
  - исключение новых аккаунтов (`min_account_age_days`);
  - минимальные пороги (`min_followers`, `min_repos`).
- Формула перспективности `0-100` по открытым метрикам:
  - followers (25%);
  - качество репозиториев по stars (25%);
  - активность за 6 месяцев (20%);
  - возраст аккаунта (15%);
  - разнообразие языков (15%).
- UI со шкалой:
  - красный `< 40`,
  - желтый `40-69`,
  - зеленый `>= 70`.

## Запуск PostgreSQL

```bash
docker compose up -d
```

## Backend запуск

1) Создай `.env` на основе `.env.example`.

2) Установи зависимости:

```bash
pip install -r requirements.txt
```

3) Запусти API:

```bash
python main.py
```

API будет доступен на `http://localhost:8000`.

## Frontend запуск

```bash
cd frontend
npm install
npm run dev
```

Frontend будет на `http://localhost:3000`.

## Основные эндпоинты

- `GET /health`
- `GET /search`
- `GET /candidates`

Пример поиска:

`/search?language=python&location=berlin&limit=10&min_followers=10&min_repos=5&min_account_age_days=365&exclude_companies=Meta&exclude_companies=Google`
