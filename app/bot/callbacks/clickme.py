from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import os
import random
import time
from datetime import datetime

from constants.general import settings, urls
from constants.protocol import addresses
from main import application
from media import stickers
from utils import onchain, tools
from services import get_dbmanager

db = get_dbmanager()


async def click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button_click_timestamp = time.time()

    current_button_data = context.bot_data.get("current_button_data")
    if (
        not current_button_data
        or update.callback_query.data != current_button_data
    ):
        return

    button_generation_timestamp = context.bot_data.get(
        "button_generation_timestamp"
    )
    if not button_generation_timestamp:
        await update.callback_query.answer("Too slow!", show_alert=True)
        return

    if context.bot_data.get("first_user_clicked"):
        await update.callback_query.answer("Too slow!", show_alert=True)
        return

    user = update.effective_user
    user_info = (
        user.username
        or f"{user.first_name} {user.last_name}"
        or user.first_name
    )

    time_taken = button_click_timestamp - button_generation_timestamp
    formatted_time_taken = tools.format_seconds(time_taken)

    await db.clicks.update(user_info, time_taken)

    context.bot_data["first_user_clicked"] = True

    user_data = await db.clicks.get(user_info)
    clicks, _, streak = user_data
    total_click_count = await db.clicks.get_total()
    burn_active = await db.settings.get("burn")

    if clicks == 1:
        user_count_message = "🎉🎉 This is their first button click! 🎉🎉"
    elif clicks % 10 == 0:
        user_count_message = f"🎉🎉 They have been the fastest Pioneer {clicks} times and on a *{streak}* click streak! 🎉🎉"
    else:
        user_count_message = f"They have been the fastest Pioneer {clicks} times and on a *{streak}* click streak!"

    if await db.clicks.is_fastest(time_taken):
        user_count_message += (
            f"\n\n🎉🎉 {formatted_time_taken} is the new fastest time! 🎉🎉"
        )

    message_text = (
        f"@{tools.escape_markdown(user_info)} was the fastest Pioneer in {formatted_time_taken}!\n\n"
        f"{user_count_message}\n\n"
        f"The button has been clicked a total of {total_click_count} times by all Pioneers!\n\n"
    )

    if burn_active:
        chain = "eth"
        clicks_needed = settings.CLICK_ME_BURN - (
            total_click_count % settings.CLICK_ME_BURN
        )
        message_text += f"Clicks till next X7R Burn: *{clicks_needed}*\n\n"

    message_text += "use `/leaderboard` to see the fastest Pioneers!"

    photos = await context.bot.get_user_profile_photos(
        update.effective_user.id, limit=1
    )
    if photos and photos.photos and photos.photos[0]:
        photo = photos.photos[0][0].file_id
        clicked = await context.bot.send_photo(
            photo=photo,
            chat_id=update.effective_chat.id,
            caption=message_text,
            parse_mode="Markdown",
        )
    else:
        clicked = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
            parse_mode="Markdown",
        )

    if burn_active and total_click_count % settings.CLICK_ME_BURN == 0:
        burn_message = await onchain.withdraw_tokens(
            int(os.getenv("TELEGRAM_ADMIN_ID")),
            settings.burn_amount(),
            settings.BURN_TOKEN,
            18,
            addresses.DEAD,
            chain,
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🔥🔥🔥🔥🔥🔥🔥🔥\n\nThe button has been clicked a total of {total_click_count} times by all Pioneers!\n\n{burn_message}",
        )

    context.bot_data["clicked_id"] = clicked.message_id
    settings.RESTART_TIME = datetime.now().timestamp()
    settings.BUTTON_TIME = settings.random_button_time()
    application.job_queue.run_once(
        send,
        settings.BUTTON_TIME,
        chat_id=urls.TG_MAIN_CHANNEL_ID,
        name="Click Me",
    )


async def send(context: ContextTypes.DEFAULT_TYPE):
    if not await db.settings.get("click_me"):
        return
    context.bot_data["first_user_clicked"] = False

    previous_click_me_id = context.bot_data.get("click_me_id")
    previous_clicked_id = context.bot_data.get("clicked_id")

    if previous_click_me_id:
        try:
            await context.bot.delete_message(
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                message_id=previous_click_me_id,
            )
            await context.bot.delete_message(
                chat_id=urls.TG_MAIN_CHANNEL_ID, message_id=previous_clicked_id
            )
        except Exception:
            pass

    current_button_data = str(random.randint(1, 100000000))
    context.bot_data["current_button_data"] = (
        f"click_button:{current_button_data}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Click Me!",
                    callback_data=context.bot_data["current_button_data"],
                )
            ]
        ]
    )
    click_me = await context.bot.send_photo(
        photo=tools.get_random_pioneer(),
        chat_id=urls.TG_MAIN_CHANNEL_ID,
        reply_markup=keyboard,
    )

    context.bot_data["button_generation_timestamp"] = time.time()
    context.bot_data["click_me_id"] = click_me.message_id


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if tools.is_admin(update.effective_user.id):
        try:
            result_text = await db.clicks.reset()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=result_text,
                message_effect_id=stickers.CONFETTI
                if query.message.chat.type == "private"
                else None,
            )
            await query.answer()
        except Exception as e:
            await query.answer(
                text=f"An error occurred: {str(e)}", show_alert=True
            )
    else:
        await query.answer(text="Admin only.", show_alert=True)
        return
