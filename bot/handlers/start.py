import os

import httpx
from telegram import Update
from telegram.ext import ContextTypes


ROLE_ALIASES = {
    "supervisor": "supervisor",
    "супервайзер": "supervisor",
    "day": "valet_day",
    "dayvalet": "valet_day",
    "дневной": "valet_day",
    "valet_day": "valet_day",
    "valetday": "valet_day",
    "night": "valet_night",
    "nightvalet": "valet_night",
    "ночной": "valet_night",
    "valet_night": "valet_night",
    "valetnight": "valet_night",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Добро пожаловать в Valet Scheduler.\n"
        "Используйте /register <Имя> <роль> для подачи заявки.\n"
        "Доступные роли: supervisor, valet_day, valet_night.\n"
        "После подтверждения администратором вы сможете выбирать смены."
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text(
            "Формат: /register <Имя> <роль>\n"
            "Пример: /register Иван valet_day"
        )
        return

    name = " ".join(args[:-1]).strip()
    raw_role = args[-1].lower()
    role = ROLE_ALIASES.get(raw_role, "valet_day")

    payload = {
        "telegram_id": update.effective_user.id,
        "username": update.effective_user.username,
        "name": name or update.effective_user.full_name,
        "role": role,
    }
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{api_url}/api/bot/users/register", json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError:
        await update.message.reply_text("Сервис сейчас недоступен. Попробуйте позже.")
        return

    await update.message.reply_text(
        f"Заявка отправлена. ID пользователя: {body.get('user_id')}\n"
        f"Роль: {role}\n"
        "Статус: ожидание подтверждения администратора."
    )
