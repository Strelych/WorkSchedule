from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_calendar(day_labels: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for index in range(0, len(day_labels), 7):
        rows.append([
            InlineKeyboardButton(day_labels[i], callback_data=f"day_{day_labels[i]}")
            for i in range(index, min(index + 7, len(day_labels)))
        ])
    return InlineKeyboardMarkup(rows)
