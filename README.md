# Valet Scheduler

Система планирования смен для валет-сервиса: Telegram-бот для управления и веб-сайт для чтения графика.

## Что уже реализовано

- каркас проекта с разделением на backend, bot и website
- конфигурация смен в [backend/shifts_config.yaml](backend/shifts_config.yaml)
- базовый FastAPI backend с роутами для бота и сайта
- генератор слотов на месяц по шаблону смен
- валидатор бизнес-правил: перекрытия, лимит мест, отдых, недельный лимит, роль/смена
- локальный docker-compose для PostgreSQL
- Telegram-бот с командами регистрации, просмотра графика и управления модерацией
- Vue 3 + Vite + Tailwind каркас интерфейса
- smoke-тесты для ключевой логики

## Архитектура

- [backend/](backend/) — FastAPI, SQLAlchemy, Alembic, сервисы и API
- [bot/](bot/) — Telegram-бот, команды и callback-обработка
- [website/](website/) — Vue 3 интерфейс для чтения графика
- [docker-compose.yml](docker-compose.yml) — PostgreSQL для локальной разработки
- [TASK.md](TASK.md) — план и статус проекта

## Быстрый старт

1. Создать виртуальное окружение:
   python -m venv .venv
   .venv\Scripts\activate
2. Установить зависимости:
   pip install -r backend/requirements.txt
3. Запустить PostgreSQL:
   docker compose up -d
4. Запустить backend:
   set PYTHONPATH=backend
   .\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend
5. Запустить Telegram-бот:
   set PYTHONPATH=.
   .\.venv\Scripts\python bot/main.py
6. Запустить сайт:
   cd website
   npm install
   npm run dev

## Проверка

Запуск базового набора тестов:

set PYTHONPATH=backend
.\.venv\Scripts\python -m pytest backend/tests -q

Проверка сборки сайта:

cd website
npm run build

Ожидаемый результат: все тесты проходят, сборка Vue завершается успешно.

## Текущее состояние

Проект находится в рабочем MVP-статусе:

- backend содержит основную логику генерации смен и валидации бизнес-правил
- бот реализует базовый сценарий регистрации и просмотра/управления графиком
- сайт представляет собой buildable каркас и готов к подключению реальных данных
- реальная БД и полноценный production-поток будут следующими шагами, когда проект будет разворачиваться в окружении

## Следующие шаги

- подключить реальную PostgreSQL через SQLAlchemy и Alembic на живом окружении
- перевести storage из in-memory в реляционную модель данных
- довести пользовательский цикл бота до полного admin/employee сценария
- закончить read-only dashboard с реальными API вызовами и фильтрами
- подготовить деплой и операционную документацию
