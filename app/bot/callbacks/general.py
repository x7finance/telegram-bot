from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes

import random

from constants.general import text
from media import stickers
from utils import tools
from services import get_dbmanager

db = get_dbmanager()


async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"{update.effective_message.text}"
    lower_message = message.lower()
    keyword_to_response = {
        "https://twitter": {
            "text": random.choice(text.X_REPLIES),
            "mode": None,
        },
        "https://x.com": {
            "text": random.choice(text.X_REPLIES),
            "mode": None,
        },
        "need developer?": {
            "text": text.CONTRIBUTE,
            "mode": None,
        },
        "gm": {"sticker": stickers.GM},
        "gm!": {"sticker": stickers.GM},
        "new on chain message": {"sticker": stickers.ONCHAIN},
        "lfg": {"sticker": stickers.LFG},
        "goat": {"sticker": stickers.GOAT},
        "smashed": {"sticker": stickers.SMASHED},
        "wagmi": {"sticker": stickers.WAGMI},
        "slapped": {"sticker": stickers.SLAPPED},
    }

    words = lower_message.split()

    for keyword, response in keyword_to_response.items():
        if keyword.startswith("https://"):
            if any(word.startswith(keyword) for word in words):
                if "text" in response:
                    await update.message.reply_text(
                        response["text"], parse_mode=response["mode"]
                    )
                elif "sticker" in response:
                    await update.message.reply_sticker(response["sticker"])
        else:
            if (
                f" {keyword} " in f" {lower_message} "
                or lower_message.startswith(keyword + " ")
                or lower_message.endswith(" " + keyword)
            ):
                if "text" in response:
                    await update.message.reply_text(
                        response["text"],
                        parse_mode=response["mode"],
                        disable_web_page_preview=True,
                    )
                elif "sticker" in response:
                    await update.message.reply_sticker(response["sticker"])


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.edit_message_text(
            text="Action canceled. No changes were made."
        )
    except Exception:
        await update.message.reply_text(
            text="Action canceled. No changes were made."
        )

    context.user_data.clear()
    return ConversationHandler.END


async def confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    amount=None,
    callback_data=None,
):
    query = update.callback_query

    callback_data = callback_data or query.data
    parts = callback_data.split(":")

    question = parts[1]
    secondary = parts[2] if len(parts) > 2 else None

    replies = {
        "clicks_reset": "Are you sure you want to reset clicks?",
        "wallet_remove": "Are you sure you want to remove your wallet? If you have funds in it, be sure you have saved the private key!",
        "stuck": "Are you sure you want to attempt to clear a stuck TX? this will send a 0 TX, but will cost gas",
    }

    reply = replies.get(question)
    yes_callback = f"{question}:{secondary}" if secondary else question

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=yes_callback),
            InlineKeyboardButton("No", callback_data="cancel"),
        ]
    ]

    await query.edit_message_text(
        text=reply, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def settings_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if tools.is_admin(query.from_user.id):
        callback_data = query.data

        setting = callback_data.replace("settings_toggle_", "")

        try:
            current_status = await db.settings.get(setting)
            new_status = not current_status
            await db.settings.set(setting, new_status)

            formatted_setting = setting.replace("_", " ").title()
            await query.answer(
                text=f"{formatted_setting} turned {'ON' if new_status else 'OFF'}."
            )

            settings = await db.settings.get_all()
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{s.replace('_', ' ').title()}: {'ON' if v else 'OFF'}",
                        callback_data=f"settings_toggle_{s}",
                    )
                ]
                for s, v in settings.items()
            ]
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "Reset Clicks", callback_data="question:clicks_reset"
                    )
                ]
            )

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_reply_markup(reply_markup=reply_markup)
        except Exception as e:
            await query.answer(text=f"Error: {e}", show_alert=True)
    else:
        await query.answer(text="Admin only.", show_alert=True)
        return


async def wallet_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        result_text = await db.wallet.remove(user_id)

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
