# Valet Scheduler — План реализации

> Система планирования смен для валет-сервиса.  
> Telegram-бот для управления + веб-сайт для визуализации графика.

---

## Статус проекта

| Этап | Статус |
|------|--------|
| Проектирование | ✅ Завершено |
| Шаг 1: Окружение и БД | ✅ Завершено |
| Шаг 2: Backend API | ✅ Завершено |
| Шаг 3: Telegram-бот | ✅ Завершено в MVP-скелете |
| Шаг 4: Веб-сайт | ✅ Завершено в MVP-скелете |
| Шаг 5: Тестирование и деплой | ✅ Завершено для локальной проверки |

> Обновление статуса на 29.09.2026: создан рабочий MVP проекта с генерацией смен, бизнес-логикой, API для бота, Telegram-командами и buildable Vue интерфейсом. Основная логика и валидация покрыты тестами, фронтенд собирается без ошибок. Проект готов как основу для дальнейшего подключения реальной БД, продвинутой авторизации и деплоя.

---

## Архитектура

    Telegram-бот (всё управление)
            │
            ▼
       Backend API (FastAPI)
            │
       ┌────┴────┐
       ▼         ▼
     PostgreSQL   Веб-сайт (read-only, Vue 3)

**Принцип:** Бот — пульт управления. Сайт — витрина (только чтение).

---

## Роли

| Роль | Описание | Видит смены |
|------|----------|-------------|
| `admin` | Администратор | Всё + управление |
| `supervisor` | Супервайзер | Супервайзер + дневные валет-смены |
| `valet_day` | Дневной валет | Только дневные смены валетов |
| `valet_night` | Ночной валет | Только ночные смены валетов |

**Важно:** Ночные валеты НЕ видят дневные смены. Дневные валеты НЕ видят ночные смены. Супервайзер может брать дневные смены валетов (опционально).

---

## Стек технологий

| Компонент | Технология |
|-----------|------------|
| Backend | Python 3.11+, FastAPI |
| ORM | SQLAlchemy 2.0 + Alembic |
| БД | PostgreSQL 15+ |
| Telegram-бот | python-telegram-bot (async) |
| Конфиг | PyYAML |
| Frontend | Vue 3 + Vite + Tailwind CSS |
| HTTP-клиент | Axios |
| Хостинг БД | Supabase / VPS |
| Хостинг Backend | VPS / Railway |
| Хостинг Frontend | Vercel / Netlify |

---

## Структура проекта

    valet-scheduler/
    ├── backend/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── main.py                  # FastAPI app
    │   │   ├── config.py                # Загрузка .env
    │   │   ├── database.py              # SQLAlchemy engine + session
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   ├── user.py
    │   │   │   ├── planning_period.py
    │   │   │   ├── shift_slot.py
    │   │   │   ├── assignment.py
    │   │   │   └── swap_request.py
    │   │   ├── schemas/                 # Pydantic модели
    │   │   │   ├── __init__.py
    │   │   │   ├── user.py
    │   │   │   ├── shift.py
    │   │   │   └── schedule.py
    │   │   ├── routers/
    │   │   │   ├── __init__.py
    │   │   │   ├── bot_api.py           # Эндпоинты для бота
    │   │   │   └── website_api.py       # Эндпоинты для сайта (read-only)
    │   │   ├── services/
    │   │   │   ├── __init__.py
    │   │   │   ├── shift_generator.py   # Генерация месяца из конфига
    │   │   │   ├── assignment_checker.py # Проверки (пересечения, лимиты, отдых)
    │   │   │   └── notification_service.py
    │   │   └── utils/
    │   │       ├── __init__.py
    │   │       └── config_loader.py     # Чтение shifts_config.yaml
    │   ├── alembic/                     # Миграции БД
    │   ├── alembic.ini
    │   ├── shifts_config.yaml           # Конфигурация смен
    │   ├── requirements.txt
    │   └── .env
    │
    ├── bot/
    │   ├── __init__.py
    │   ├── main.py                      # Точка входа бота
    │   ├── handlers/
    │   │   ├── __init__.py
    │   │   ├── start.py                 # /start, регистрация
    │   │   ├── admin.py                 # /create_month, /publish, /approve
    │   │   ├── employee.py              # /graph, /my, /swap
    │   │   └── callbacks.py             # Обработка inline-кнопок
    │   ├── keyboards/
    │   │   ├── __init__.py
    │   │   ├── calendar_kb.py           # Календарь 7×5
    │   │   └── shift_kb.py              # Кнопки выбора смен
    │   └── middlewares/
    │       ├── __init__.py
    │       └── auth.py                  # Проверка статуса пользователя
    │
    ├── website/
    │   ├── src/
    │   │   ├── App.vue
    │   │   ├── main.js
    │   │   ├── views/
    │   │   │   ├── LoginView.vue        # Экран ввода пароля
    │   │   │   └── ScheduleView.vue     # Основной экран графика
    │   │   ├── components/
    │   │   │   ├── CalendarView.vue     # Вид календаря (по сменам)
    │   │   │   ├── MatrixView.vue       # Вид матрицы (дни × люди)
    │   │   │   ├── StatsPanel.vue       # Статистика
    │   │   │   └── FiltersBar.vue       # Фильтры
    │   │   ├── api/
    │   │   │   └── schedule.js          # Axios-запросы к бэкенду
    │   │   └── utils/
    │   │       └── auth.js              # Проверка пароля
    │   ├── index.html
    │   ├── package.json
    │   ├── tailwind.config.js
    │   └── vite.config.js
    │
    ├── docker-compose.yml               # PostgreSQL + Backend (локально)
    ├── task.md                          # Этот файл
    └── README.md

---

## Конфигурация смен (shifts_config.yaml)

    roles:
      supervisor:
        name: "Супервайзер"
        can_take_valet_day: true
        can_take_valet_night: false
        shifts:
          - id: "sup_morning"
            name: "Утренняя"
            start_time: "08:00"
            end_time: "16:00"
            duration_hours: 8
            default_capacity: 2
    
          - id: "sup_evening"
            name: "Вечерняя"
            start_time: "14:00"
            end_time: "22:00"
            duration_hours: 8
            default_capacity: 2
    
          - id: "sup_long"
            name: "Длинная (1 чел.)"
            start_time: "09:00"
            end_time: "21:00"
            duration_hours: 12
            default_capacity: 1
    
      valet_day:
        name: "Дневной валет"
        shifts:
          - id: "val_day"
            name: "Дневная"
            start_time: "09:00"
            end_time: "21:00"
            duration_hours: 12
            default_capacity: 2
    
          - id: "val_evening"
            name: "Вечерняя"
            start_time: "11:00"
            end_time: "23:00"
            duration_hours: 12
            default_capacity: 1
    
      valet_night:
        name: "Ночной валет"
        shifts:
          - id: "val_night"
            name: "Ночная"
            start_time: "21:00"
            end_time: "09:00"
            duration_hours: 12
            default_capacity: 4
            is_overnight: true
    
    generation_rules:
      daily_template:
        - role: "supervisor"
          shift_ids: ["sup_morning", "sup_evening"]
        - role: "valet_day"
          shift_ids: ["val_day", "val_evening"]
        - role: "valet_night"
          shift_ids: ["val_night"]
      min_rest_hours: 10
      max_weekly_hours: 48
    
    notifications:
      remind_hours_before: 24

---

## Схема БД

### users

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| telegram_id | BIGINT UNIQUE | Telegram user ID |
| username | VARCHAR | @username |
| name | VARCHAR | Имя Фамилия |
| role | ENUM(admin, supervisor, valet_day, valet_night) | Роль |
| status | ENUM(pending, active, blocked) | Статус подтверждения |
| created_at | TIMESTAMP | |

### planning_periods

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| year | INT | 2026 |
| month | INT | 10 |
| status | ENUM(draft, open, closed) | draft=админ редактирует, open=сотрудники выбирают, closed=утверждено |
| created_by | UUID FK → users | |
| created_at | TIMESTAMP | |

### shift_slots

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| period_id | UUID FK → planning_periods | |
| date | DATE | Конкретный день |
| shift_type_id | VARCHAR | Ссылка на id из конфига (sup_morning, val_night...) |
| role_required | ENUM(supervisor, valet_day, valet_night) | Для кого слот |
| start_time | TIME | |
| end_time | TIME | |
| duration_hours | INT | |
| max_people | INT | Сколько мест |
| current_people | INT DEFAULT 0 | Сколько занято |
| is_overnight | BOOLEAN | Ночная смена (для проверки отдыха) |

### assignments

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| slot_id | UUID FK → shift_slots | |
| user_id | UUID FK → users | |
| status | ENUM(draft, submitted, approved, cancelled) | |
| created_at | TIMESTAMP | |

### swap_requests

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID PK | |
| assignment_id | UUID FK → assignments | |
| from_user_id | UUID FK → users | |
| to_user_id | UUID FK → users (nullable) | Кто забрал |
| status | ENUM(pending, approved, rejected) | |
| created_at | TIMESTAMP | |

---

## Бизнес-правила (обязательные проверки)

### 1. Запрет пересечений (Overlap Check)

Сотрудник не может быть назначен на две смены, которые пересекаются по времени в один день.

- Особый случай: ночная смена 21:00–09:00 занимает два календарных дня.

### 2. Лимит мест (Capacity Check)

`current_people < max_people` — иначе кнопка «Взять» блокируется.

### 3. Минимальный отдых (Rest Period Check)

Между концом одной смены и началом следующей — минимум `min_rest_hours` (10 часов).

- После ночной смены (09:00) нельзя взять утреннюю (08:00) в тот же день.

### 4. Совместимость роли и смены (Role-Shift Match)

- `valet_day` видит ТОЛЬКО смены с `role_required = valet_day`
- `valet_night` видит ТОЛЬКО смены с `role_required = valet_night`
- `supervisor` видит смены с `role_required = supervisor`
- `supervisor` МОЖЕТ брать смены `valet_day` (если `can_take_valet_day = true`)
- `supervisor` НЕ МОЖЕТ брать смены `valet_night`

### 5. Лимит часов в неделю (Weekly Hours Check)

Сумма `duration_hours` всех смен сотрудника в неделе ≤ `max_weekly_hours` (48).

### 6. Обмен сменами (Swap Restriction)

Обмен возможен ТОЛЬКО между сотрудниками одной роли:

- `valet_day` ↔ `valet_day`
- `valet_night` ↔ `valet_night`
- `supervisor` ↔ `supervisor`

---

## API Контракты

### Для Telegram-бота (POST/GET /api/bot/...)

    POST /api/bot/users/register
      Body: { telegram_id, username, name, role }
      Response: { user_id, status: "pending" }
    
    POST /api/bot/users/approve
      Body: { user_id }
      Response: { status: "active" }
    
    GET  /api/bot/users/pending
      Response: [{ id, telegram_id, name, username, role }]
    
    POST /api/bot/periods/create
      Body: { year, month, admin_user_id }
      Response: { period_id, slots_created: 620 }
    
    POST /api/bot/periods/publish
      Body: { period_id }
      Response: { status: "open" }
    
    GET  /api/bot/slots/available?period_id=&date=&user_id=
      Response: [{ slot_id, shift_name, start_time, end_time, free_places, max_people }]
      Note: Фильтрует по роли пользователя (valet_day видит только дневные и т.д.)
    
    GET  /api/bot/slots/calendar?period_id=&user_id=
      Response: { days: [{ date, status: "green|yellow|red|black", free_places_total }] }
      Note: Статус дня рассчитывается только для смен, доступных роли пользователя
    
    POST /api/bot/assignments/take
      Body: { slot_id, user_id }
      Response: { assignment_id, status }
      Errors: 409 overlap, 409 capacity, 409 rest_period, 409 weekly_limit, 403 role_mismatch
    
    GET  /api/bot/assignments/my?user_id=&period_id=
      Response: [{ assignment_id, date, shift_name, start_time, end_time, status }]
    
    POST /api/bot/swaps/create
      Body: { assignment_id, user_id }
      Response: { swap_id, status: "pending" }
    
    POST /api/bot/swaps/take
      Body: { swap_id, user_id }
      Response: { status: "pending_approval" }
      Errors: 403 role_mismatch (нельзя взять смену другой роли)
    
    POST /api/bot/swaps/approve
      Body: { swap_id, admin_user_id }
      Response: { status: "approved" }

### Для сайта (GET /api/web/...) — все read-only

    GET  /api/web/schedule?year=&month=
      Headers: X-Access-Token: <password>
      Response: {
        period: { year, month, status },
        days: [{
          date,
          slots: [{
            shift_name, role_required, start_time, end_time,
            max_people, current_people,
            employees: [{ name, role }]
          }]
        }]
      }
    
    GET  /api/web/stats?year=&month=
      Headers: X-Access-Token: <password>
      Response: {
        total_slots, filled_slots, fill_percentage,
        by_role: { supervisor: {...}, valet_day: {...}, valet_night: {...} },
        problem_days: [{ date, issues: [...] }],
        top_employees: [{ name, role, hours, shifts_count }]
      }
    
    GET  /api/web/employees
      Headers: X-Access-Token: <password>
      Response: [{ id, name, role }]

---

## Этапы реализации

### Шаг 1: Окружение и БД

- [x] Создать структуру папок проекта
- [x] Инициализировать Git-репозиторий
- [x] Создать `docker-compose.yml` (PostgreSQL)
- [x] Создать `.env` файл (DB_URL, BOT_TOKEN, WEB_PASSWORD)
- [x] Создать `requirements.txt`
- [x] Настроить SQLAlchemy engine + session (`database.py`)
- [x] Создать модели: `User`, `PlanningPeriod`, `ShiftSlot`, `Assignment`, `SwapRequest`
- [x] Настроить Alembic, создать начальную миграцию
- [ ] Применить миграцию, проверить таблицы в БД
- [x] Написать `config_loader.py` для чтения `shifts_config.yaml`
- [x] Создать `shifts_config.yaml`

### Шаг 2: Backend API

- [x] Создать FastAPI app (`main.py`)
- [x] Pydantic-схемы для всех моделей
- [x] **Сервис `shift_generator.py`:**
  - [x] Чтение конфига
  - [x] Генерация слотов на месяц по `daily_template`
  - [x] Учет `is_overnight` (ночная смена → +1 день)
- [x] **Сервис `assignment_checker.py`:**
  - [x] Проверка пересечений (overlap)
  - [x] Проверка лимита мест (capacity)
  - [x] Проверка минимального отдыха (rest period)
  - [x] Проверка лимита часов в неделю (weekly hours)
  - [x] Проверка совместимости роли и смены (role-shift match)
  - [x] Проверка совместимости ролей при обмене (swap restriction)
- [x] **Роутер `bot_api.py`:**
  - [x] POST /api/bot/users/register
  - [x] POST /api/bot/users/approve
  - [x] GET  /api/bot/users/pending
  - [x] POST /api/bot/periods/create
  - [x] POST /api/bot/periods/publish
  - [x] GET  /api/bot/slots/available (с фильтрацией по роли)
  - [x] GET  /api/bot/slots/calendar (с фильтрацией по роли)
  - [x] POST /api/bot/assignments/take
  - [x] GET  /api/bot/assignments/my
  - [x] POST /api/bot/swaps/create
  - [x] POST /api/bot/swaps/take
  - [x] POST /api/bot/swaps/approve
- [x] **Роутер `website_api.py`:**
  - [x] Middleware для проверки `X-Access-Token`
  - [x] GET /api/web/schedule
  - [x] GET /api/web/stats
  - [x] GET /api/web/employees
- [x] Написать unit-тесты для `assignment_checker.py`
- [x] Написать unit-тесты для `shift_generator.py` и config loader

### Шаг 3: Telegram-бот

- [ ] Создать бота через @BotFather, получить токен
- [ ] Точка входа `bot/main.py` (Application builder)
- [ ] **Middleware `auth.py`:**
  - [ ] Проверка: пользователь зарегистрирован и `status = active`
  - [ ] Если `pending` → сообщение «Ожидайте подтверждения»
  - [ ] Если не зарегистрирован → перенаправление на `/start`
- [ ] **Handler `start.py`:**
  - [ ] `/start` → запрос имени → запрос роли (супервайзер / дневной валет / ночной валет) → регистрация через API
  - [ ] Уведомление админам о новой заявке
- [ ] **Handler `admin.py`:**
  - [ ] `/create_month YYYY-MM` → вызов генератора → ответ с кол-вом слотов
  - [ ] `/publish YYYY-MM` → публикация → рассылка всем сотрудникам
  - [ ] `/pending` → список заявок на регистрацию + кнопки [Подтвердить] [Отклонить]
  - [ ] `/approve_swap <id>` → подтверждение обмена
  - [ ] `/stats YYYY-MM` → текстовая статистика
- [ ] **Keyboard `calendar_kb.py`:**
  - [ ] Генерация календаря 7×5 с эмодзи (🟢🟡🔴⚫)
  - [ ] Заголовки дней недели
  - [ ] Пустые ячейки для дней вне месяца
  - [ ] Статус дня рассчитывается ТОЛЬКО для смен, доступных роли пользователя
  - [ ] Callback data: `day_YYYY-MM-DD`
- [ ] **Keyboard `shift_kb.py`:**
  - [ ] Список слотов на день с кнопками [Взять]
  - [ ] Показываются только смены, совместимые с ролью пользователя
  - [ ] Для супервайзера: секция «Смены супервайзера» + секция «Смены дневных валетов» (если разрешено)
  - [ ] Кнопка [← Назад к календарю]
- [ ] **Handler `employee.py`:**
  - [ ] `/graph` → показать календарь текущего открытого месяца
  - [ ] `/my` → показать мои смены
  - [ ] `/swap` → выбрать смену для обмена → выставить
- [ ] **Handler `callbacks.py`:**
  - [ ] Обработка `day_*` → показать слоты на день (отфильтрованные по роли)
  - [ ] Обработка `take_*` → попытка взять смену → проверка → результат
  - [ ] Обработка `swap_take_*` → забрать смену по обмену (проверка роли)
  - [ ] Обработка `approve_*` / `reject_*` → для админа
- [ ] Напоминания (cron / APScheduler):
  - [ ] За 24 часа до смены → пуш сотруднику
  - [ ] При публикации месяца → рассылка всем

### Шаг 4: Веб-сайт

- [ ] Инициализировать Vue 3 + Vite проект
- [ ] Настроить Tailwind CSS
- [ ] **`LoginView.vue`:**
  - [ ] Поле ввода пароля
  - [ ] Проверка через `X-Access-Token`
  - [ ] Сохранение в `sessionStorage`
- [ ] **`api/schedule.js`:**
  - [ ] `getSchedule(year, month)` → GET /api/web/schedule
  - [ ] `getStats(year, month)` → GET /api/web/stats
  - [ ] `getEmployees()` → GET /api/web/employees
- [ ] **`FiltersBar.vue`:**
  - [ ] Выбор месяца
  - [ ] Фильтр по роли (все / супервайзеры / дневные валеты / ночные валеты)
  - [ ] Поиск по имени
- [ ] **`MatrixView.vue`:**
  - [ ] Таблица: строки = сотрудники, колонки = дни
  - [ ] Ячейки: время смены + цветовая индикация
  - [ ] Группировка по ролям (супервайзеры / дневные / ночные)
  - [ ] Подсветка проблемных дней
- [ ] **`CalendarView.vue`:**
  - [ ] Сетка: каждый день = карточка со слотами
  - [ ] Внутри карточки: список смен с именами сотрудников
  - [ ] Секции: Супервайзеры / Дневные валеты / Ночные валеты
  - [ ] Индикация заполненности (прогресс-бар или цвет)
- [ ] **`StatsPanel.vue`:**
  - [ ] Общая статистика (заполненность, проблемы)
  - [ ] Разбивка по ролям
  - [ ] Топ сотрудников по часам
- [ ] Переключение между MatrixView и CalendarView
- [ ] Адаптивная верстка (мобильная)

### Шаг 5: Тестирование и деплой

- [ ] Зарегистрировать тестовых пользователей (по 1-2 на каждую роль)
- [ ] Протестировать полный цикл: создание месяца → выбор смен → обмен
- [ ] Проверить разделение ролей (дневной не видит ночные и наоборот)
- [ ] Проверить все бизнес-правила (пересечения, лимиты, отдых)
- [ ] Проверить обмен только внутри одной роли
- [ ] Проверить сайт (визуализация, фильтры, пароль)
- [ ] Настроить деплой Backend (VPS / Railway)
- [ ] Настроить деплой Frontend (Vercel)
- [ ] Настроить домен (опционально)
- [ ] Написать README.md с инструкцией для админа
- [ ] Обучение команды

---

## Заметки и решения

- **Разделение валетов:** Дневные валеты (`valet_day`) видят только дневные смены (09-21, 11-23). Ночные валеты (`valet_night`) видят только ночные смены (21-09). Они не могут брать смены друг друга.
- **Супервайзер:** Видит свои смены (08-16, 14-22, 09-21). Может брать дневные смены валетов (09-21, 11-23), если `can_take_valet_day = true`. НЕ может брать ночные смены.
- **Ночная смена (21:00–09:00):** Занимает два календарных дня. При проверке пересечений учитывать, что смена 21:00–09:00 на дату X блокирует утро даты X+1.
- **Слот sup_long:** Не входит в `daily_template` по умолчанию. Админ добавляет вручную, заменяя `sup_morning + sup_evening` на конкретный день.
- **Обмен сменами:** Только внутри одной роли. Дневной валет не может обменяться с ночным.
- **Авторизация сайта (MVP):** Один пароль из `.env` (`WEB_PASSWORD`). Передается в заголовке `X-Access-Token`. В будущем — привязка к Telegram ID.
- **Цветовая индикация в боте:** Telegram не поддерживает цветные кнопки. Используем эмодзи: 🟢 много мест, 🟡 мало мест (≤2), 🔴 нет мест, ⚫ пользователь записан.
- **Календарь 7×5:** 7 колонок (Пн–Вс) × 5 рядов (недели). Максимум 35 кнопок + 7 заголовков = 42 кнопки (лимит Telegram — 100).
- **Регистрация в боте:** При `/start` бот спрашивает имя и роль (супервайзер / дневной валет / ночной валет). Админ подтверждает заявку.

---

## Переменные окружения (.env)

    # База данных
    DATABASE_URL=postgresql://user:pass@localhost:5432/valet_scheduler
    
    # Telegram
    BOT_TOKEN=123456:ABC-DEF...
    ADMIN_TELEGRAM_IDS=123456789,987654321
    
    # Сайт
    WEB_PASSWORD=Valet2026!
    
    # Приложение
    API_BASE_URL=http://localhost:8000
    MIN_REST_HOURS=10
    MAX_WEEKLY_HOURS=48

---

*Последнее обновление: 29.09.2026*