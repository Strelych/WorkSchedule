import os

import httpx
from telegram import Update
from telegram.ext import ContextTypes


async def my_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{api_url}/api/bot/assignments/my",
                params={"user_id": user_id, "period_id": "period_1"},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        await update.message.reply_text("Не удалось загрузить смены.")
        return

    if not data:
        await update.message.reply_text("У вас пока нет назначенных смен.")
        return

    lines = ["Ваши смены:"]
    for entry in data:
        lines.append(f"- {entry['date']} {entry['shift_name']} ({entry['start_time']}–{entry['end_time']})")
    await update.message.reply_text("\n".join(lines))


async def graph_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_url}/api/bot/slots/calendar", params={"period_id": "period_1", "user_id": str(update.effective_user.id)})
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        await update.message.reply_text("Не удалось загрузить календарь.")
        return

    days = data.get("days", [])
    if not days:
        await update.message.reply_text("Календарь для этого месяца пустой.")
        return

    lines = ["Календарь доступных дней:"]
    for day in days:
        lines.append(f"- {day['date']}: {day['status']} ({day['free_places_total']} мест)")
    await update.message.reply_text("\n".join(lines))
