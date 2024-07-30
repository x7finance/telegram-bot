from telegram import *
from telegram.ext import *

import os
from datetime import datetime, timedelta

from hooks import  db, api
from variables import times

defined = api.Defined()


async def everyone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.effective_chat.id
    if str(channel_id) == os.getenv("DAO_TELEGRAM_CHANNEL_ID"):
        administrators = await context.bot.get_chat_administrators(os.getenv("DAO_TELEGRAM_CHANNEL_ID"))
        members = [f"@{admin.user.username}" for admin in administrators]
        message = await update.message.reply_text(
            "\n".join(members),
        )
        await context.bot.edit_message_text("ALL DAO MENTIONED", channel_id, message.id, )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("OWNER_TELEGRAM_CHANNEL_ID")):
        reset_text = db.clicks_reset()
        await update.message.reply_text(f"{reset_text}")


async def wen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == int(os.getenv("OWNER_TELEGRAM_CHANNEL_ID")):
        if update.effective_chat.type == "private":
            if times.BUTTON_TIME is not None:
                time = times.BUTTON_TIME
            else:    
                time = times.FIRST_BUTTON_TIME
            target_timestamp = times.RESTART_TIME + time
            time_difference_seconds = target_timestamp - datetime.now().timestamp()
            time_difference = timedelta(seconds=time_difference_seconds)
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            await update.message.reply_text(f"Next Click Me:\n\n{hours} hours, {minutes} minutes, {seconds} seconds\n\n"
            )