from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from datetime import datetime

from media import stickers
from utils import tools
from services import get_dbmanager

db = get_dbmanager()


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    _, number = query.data.split(":")

    try:
        reminder_num = int(number)
        reminders = await db.reminders.get(user.id)

        if (
            not reminders
            or reminder_num < 1
            or reminder_num > len(reminders["reminders"])
        ):
            await query.answer("Invalid reminder number!")
            return

        reminder_to_remove = reminders["reminders"][reminder_num - 1]
        when = datetime.strptime(
            reminder_to_remove["time"], "%Y-%m-%d %H:%M:%S"
        )

        await db.reminders.remove(user.id, when)

        job_name = f"reminder_{user.id}_{when.strftime('%Y-%m-%d %H:%M:%S')}"
        for job in context.job_queue.get_jobs_by_name(job_name):
            job.schedule_removal()

        updated_reminders = await db.reminders.get(user.id)
        if updated_reminders and updated_reminders["reminders"]:
            reminder_list = "\n\n".join(
                f"#{i + 1}\n📅 {r['time']}\n💭 {r['message']}"
                for i, r in enumerate(updated_reminders["reminders"])
            )

            buttons = []
            reminder_buttons = []
            for i in range(len(updated_reminders["reminders"])):
                reminder_buttons.append(
                    InlineKeyboardButton(
                        text=f"Remove #{i + 1}",
                        callback_data=f"reminder_remove:{i + 1}",
                    )
                )

            for i in range(0, len(reminder_buttons), 3):
                buttons.append(reminder_buttons[i : i + 3])

            markup = InlineKeyboardMarkup(buttons)

            await query.message.edit_text(
                f"Your current reminders ({len(updated_reminders['reminders'])}/3):\n\n{reminder_list}\n\n"
                "All times are UTC",
                reply_markup=markup,
            )
        else:
            await query.message.edit_text("No reminders set (0/3).")

        await query.answer(f"Reminder #{reminder_num} removed!")

    except (ValueError, IndexError):
        await query.answer("Error removing reminder!")


async def send(context: ContextTypes.DEFAULT_TYPE):
    reminder = context.job.data
    when = datetime.strptime(reminder["reminder_time"], "%Y-%m-%d %H:%M:%S")

    await context.bot.send_message(
        chat_id=reminder["user_id"],
        text=(
            f"🚨 *REMINDER - {when}* 🚨\n\n{tools.escape_markdown(reminder['message'])}"
        ),
        message_effect_id=stickers.CONFETTI,
        parse_mode="Markdown",
    )

    await db.reminders.remove(reminder["user_id"], when)


async def set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_callback = hasattr(update, "callback_query") and update.callback_query

    if is_callback:
        user = update.callback_query.from_user
        data = update.callback_query.data
        chat_id = update.callback_query.message.chat.id
    else:
        user = update.effective_user
        data = context.user_data.get("reminder_data")
        chat_id = update.effective_chat.id

    wallet = await db.wallet.get(user.id)
    if not wallet:
        if is_callback:
            await update.callback_query.answer(
                "Use /register to use this service", show_alert=True
            )
        else:
            await update.message.reply_text(
                "Use /register to use this service"
            )
        return

    data_parts = data.split(":")

    if data_parts[1] == "loan":
        date = f"{data_parts[2]}:{data_parts[3]}:{data_parts[4]}"
        amount = data_parts[5]
        loan_id = data_parts[6]
        chain = data_parts[7]
        message = f"{amount} due on Loan ID {chain.upper()}: {loan_id}"

    elif data_parts[1] == "lock":
        date = f"{data_parts[2]}:{data_parts[3]}:{data_parts[4]}"
        chain = data_parts[6]

        if not data_parts[5]:
            message = f"Global lock expired on {chain.upper()}"
        else:
            message = f"{data_parts[5]} lock expired on {chain.upper()}"

    elif data_parts[1] == "manual":
        date = f"{data_parts[2]}:{data_parts[3]}:{data_parts[4]}"
        message = data_parts[5]

    when = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    reminders = await db.reminders.get(user.id)
    if reminders and reminders["reminders"]:
        reminder_time = when.strftime("%Y-%m-%d %H:%M:%S")
        for reminder in reminders["reminders"]:
            if (
                reminder["time"] == reminder_time
                and reminder["message"] == message
            ):
                reply_text = "You already have a reminder set for this event!\n\nUse /reminders to view your reminders"
                if is_callback:
                    await update.callback_query.answer(
                        reply_text,
                        show_alert=True,
                    )
                else:
                    await update.message.reply_text(reply_text)
                return

    if reminders and len(reminders["reminders"]) >= 3:
        reply_text = "You've reached the maximum limit of 3 reminders.\n\nUse /reminders to view your reminders and remove one if you need to."
        if is_callback:
            await update.callback_query.answer(
                reply_text,
                show_alert=True,
            )
        else:
            await update.message.reply_text(reply_text)
        return

    await db.reminders.add(user.id, when, message)

    job_name = f"reminder_{user.id}_{when.strftime('%Y-%m-%d %H:%M:%S')}"
    context.job_queue.run_once(
        callback=send,
        when=when,
        data={
            "chat_id": chat_id,
            "user_id": user.id,
            "message": message,
            "reminder_time": when.strftime("%Y-%m-%d %H:%M:%S"),
        },
        name=job_name,
    )

    current_count = len(reminders["reminders"]) + 1 if reminders else 1
    reply_text = f"✅ Reminder set! ({current_count}/3)\n\nUse /reminders to view your reminders"
    if is_callback:
        await update.callback_query.answer(reply_text, show_alert=True)
    else:
        await update.message.reply_text(
            reply_text, message_effect_id=stickers.CONFETTI
        )
