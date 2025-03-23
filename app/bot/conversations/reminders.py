from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes

from datetime import datetime

from bot import callbacks
from utils import tools
from services import get_dbmanager


db = get_dbmanager()


DATE, TIME, MESSAGE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    calendar_markup = tools.create_calendar_keyboard(now.year, now.month)

    await update.callback_query.message.edit_text(
        "Please select a date for your reminder:", reply_markup=calendar_markup
    )
    await update.callback_query.answer()

    return DATE


async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, *data = query.data.split(":")

    if action == "ignore":
        await query.answer()
        return DATE

    if action in ["cal_prev", "cal_next"]:
        year, month = map(int, data)
        if action == "cal_prev":
            month -= 1
            if month < 1:
                month = 12
                year -= 1
        else:
            month += 1
            if month > 12:
                month = 1
                year += 1

        calendar_markup = tools.create_calendar_keyboard(year, month)
        await query.message.edit_reply_markup(reply_markup=calendar_markup)
        await query.answer()
        return DATE

    if action == "date":
        year, month, day = map(int, data)

        selected_date = datetime(year, month, day)
        now = datetime.now()
        if selected_date.date() < now.date():
            await query.answer("Cannot set reminders in the past!")
            return DATE

        context.user_data["reminder_date"] = (year, month, day)
        time_keyboard = tools.create_time_keyboard()
        await query.message.edit_text(
            f"Selected date: {month}/{day}/{year}\nPlease select a time:",
            reply_markup=time_keyboard,
        )
        return TIME


async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(":")

    if len(data) != 3 or data[0] != "time":
        await query.answer("Invalid selection")
        return TIME

    try:
        hour = int(data[1])
        minute = int(data[2])
        year, month, day = context.user_data["reminder_date"]
        when = datetime(year, month, day, hour, minute)

        now = datetime.now()
        if when <= now:
            await query.answer("Cannot set reminders in the past!")
            return TIME

        context.user_data["reminder_time"] = when
        await query.message.edit_text(
            f"Selected: {when.strftime('%m/%d/%Y %H:%M')}\n"
            "Please enter your reminder message:"
        )
        return MESSAGE

    except (ValueError, KeyError):
        await query.answer("Invalid time selection")
        return TIME


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminder_message = update.message.text
    when = context.user_data["reminder_time"]

    if len(reminder_message) > 200:
        await update.message.reply_text(
            f"Message too long ({len(reminder_message)} characters).\n"
            "Please limit your message to 200 characters."
        )
        return MESSAGE

    context.user_data["reminder_data"] = (
        f"reminder:manual:{when.strftime('%Y-%m-%d %H:%M:%S')}:{reminder_message}"
    )

    await callbacks.reminders.set(update, context)

    return ConversationHandler.END
