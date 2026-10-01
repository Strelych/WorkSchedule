import os

import httpx
from telegram import Update
from telegram.ext import ContextTypes


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    callback = update.callback_query
    if callback is None:
        return

    if callback.data is None:
        await callback.answer("Пустой callback", show_alert=True)
        return

    await callback.answer("Обрабатываю выбор...")

    if callback.data.startswith("day_"):
        day = callback.data.replace("day_", "", 1)
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{api_url}/api/bot/slots/available",
                    params={"period_id": "period_1", "date": day, "user_id": str(callback.from_user.id)},
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            await callback.message.reply_text("Не удалось загрузить доступные смены.")
            return

        if not data:
            await callback.message.reply_text(f"На {day} нет доступных смен.")
            return

        lines = [f"Смены на {day}:"]
        for slot in data:
            lines.append(f"- {slot['shift_name']} {slot['start_time']}–{slot['end_time']} ({slot['free_places']}/{slot['max_people']})")
        await callback.message.reply_text("\n".join(lines))
        return

    if callback.data.startswith("take_"):
        slot_id = callback.data.replace("take_", "", 1)
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{api_url}/api/bot/assignments/take",
                    json={"slot_id": slot_id, "user_id": str(callback.from_user.id)},
                )
                body = response.json()
                response.raise_for_status()
        except httpx.HTTPError:
            await callback.message.reply_text("Не удалось записаться на смену.")
            return

        await callback.message.reply_text(f"Вы записаны на смену. assignment_id: {body.get('assignment_id')}")
        return

    await callback.message.reply_text("Действие не распознано.")
