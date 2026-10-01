from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_shift_keyboard(slots: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for slot in slots:
        label = f"{slot.get('shift_name', 'Shift')} {slot.get('start_time', '')}-{slot.get('end_time', '')}"
        rows.append([InlineKeyboardButton(label, callback_data=f"take_{slot.get('slot_id', '')}")])
    return InlineKeyboardMarkup(rows)
