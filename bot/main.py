import os

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.handlers.admin import approve_user, create_month, pending_users
from bot.handlers.callbacks import handle_callback
from bot.handlers.employee import graph_schedule, my_schedule
from bot.handlers.start import register, start

TOKEN = os.getenv("BOT_TOKEN", "token-placeholder")
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("register", register))
app.add_handler(CommandHandler("create_month", create_month))
app.add_handler(CommandHandler("pending", pending_users))
app.add_handler(CommandHandler("approve", approve_user))
app.add_handler(CommandHandler("my", my_schedule))
app.add_handler(CommandHandler("graph", graph_schedule))
app.add_handler(CallbackQueryHandler(handle_callback))


if __name__ == "__main__":
    app.run_polling()
