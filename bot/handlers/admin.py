import os

import httpx
from telegram import Update
from telegram.ext import ContextTypes


async def create_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if len(args) != 1:
        await update.message.reply_text("Формат: /create_month 2026-10")
        return

    year_month = args[0]
    try:
        year, month = [int(part) for part in year_month.split("-")]
    except ValueError:
        await update.message.reply_text("Ошибка генерации месяца. Проверьте формат: YYYY-MM")
        return

    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{api_url}/api/bot/periods/create",
                json={"year": year, "month": month, "admin_user_id": str(update.effective_user.id)},
            )
            body = response.json()
            response.raise_for_status()
    except httpx.HTTPError:
        await update.message.reply_text("Не удалось создать период. Проверьте API и подключение.")
        return

    await update.message.reply_text(f"Период создан. Создано слотов: {body.get('slots_created', 0)}")


async def pending_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_url}/api/bot/users/pending")
            response.raise_for_status()
            users = response.json()
    except httpx.HTTPError:
        await update.message.reply_text("Не удалось получить список заявок.")
        return

    if not users:
        await update.message.reply_text("Новых заявок нет.")
        return

    lines = ["Заявки на регистрацию:"]
    for user in users:
        lines.append(f"- {user['name']} ({user['role']}) / {user['telegram_id']}")
    await update.message.reply_text("\n".join(lines))


async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []
    if len(args) != 1:
        await update.message.reply_text("Формат: /approve <user_id>")
        return

    user_id = args[0]
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{api_url}/api/bot/users/approve", json={"user_id": user_id})
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError:
        await update.message.reply_text("Не удалось подтвердить пользователя.")
        return

    await update.message.reply_text(f"Пользователь {user_id} подтверждён. Статус: {body.get('status')}")
