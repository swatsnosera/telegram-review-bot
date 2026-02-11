from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

import os
TOKEN = os.getenv("7979765433:AAE0mzKNx7uNqE68mRq0kaud4Om2XlmsooI")
CHANNEL_USERNAME = "@BEYWOIP"

RATING, REVIEW, ASK_CONS, CONS_TEXT = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("⭐️", callback_data="1"),
        InlineKeyboardButton("⭐️⭐️", callback_data="2"),
        InlineKeyboardButton("⭐️⭐️⭐️", callback_data="3"),
        InlineKeyboardButton("⭐️⭐️⭐️⭐️", callback_data="4"),
        InlineKeyboardButton("⭐️⭐️⭐️⭐️⭐️", callback_data="5"),
    ]]
    await update.message.reply_text(
        "Оцените услугу от 1 до 5 ⭐️",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return RATING


async def rating_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    stars = int(query.data)
    rating_display = "★" * stars + "☆" * (5 - stars)

    context.user_data["rating"] = rating_display
    context.user_data["stars_count"] = stars

    await query.message.reply_text("Напишите текст отзыва 📝")
    return REVIEW


async def review_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["review_text"] = update.message.text

    keyboard = [[
        InlineKeyboardButton("Есть", callback_data="yes"),
        InlineKeyboardButton("Нет", callback_data="no"),
    ]]
    await update.message.reply_text(
        "Есть ли минусы или замечания?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ASK_CONS


async def ask_cons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "no":
        context.user_data["cons_text"] = "Замечаний нет"
        await publish_review(query, context)
        return ConversationHandler.END
    else:
        await query.message.reply_text("Напишите, что можно улучшить 🔍")
        return CONS_TEXT


async def cons_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cons_text"] = update.message.text
    await publish_review(update, context)
    return ConversationHandler.END


async def publish_review(source, context: ContextTypes.DEFAULT_TYPE):
    user = source.from_user
    username = f"@{user.username}" if user.username else user.first_name

    review_message = (
        f"👤 Клиент: {username}\n"
        f"🆔 ID клиента: {user.id}\n\n"
        f"⭐️ Оценка сервиса: {context.user_data['rating']} "
        f"({context.user_data['stars_count']} из 5)\n\n"
        f"💬 **Впечатления:**\n"
        f"{context.user_data['review_text']}\n\n"
        f"🔍 **Что можно улучшить:**\n"
        f"{context.user_data['cons_text']}"
    )

    await context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=review_message,
        parse_mode="Markdown"
    )

    if hasattr(source, "message"):
        await source.message.reply_text("Спасибо за отзыв! ❤️ Он опубликован в канале.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отзыв отменён.")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            RATING: [CallbackQueryHandler(rating_chosen)],
            REVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_received)],
            ASK_CONS: [CallbackQueryHandler(ask_cons)],
            CONS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, cons_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
