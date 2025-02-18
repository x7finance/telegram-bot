from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes

import os
import time
from datetime import datetime

from bot import auto, callbacks
from constants.bot import settings, urls
from constants.protocol import addresses, chains, splitters
from main import application
from utils import onchain, tools
from services import get_dbmanager

db = get_dbmanager()


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


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    db.clicks_update(user_info, time_taken)

    context.bot_data["first_user_clicked"] = True

    user_data = db.clicks_get_by_name(user_info)
    clicks, _, streak = user_data
    total_click_count = db.clicks_get_total()
    burn_active = db.settings_get("burn")

    if clicks == 1:
        user_count_message = "🎉🎉 This is their first button click! 🎉🎉"
    elif clicks % 10 == 0:
        user_count_message = f"🎉🎉 They have been the fastest Pioneer {clicks} times and on a *{streak}* click streak! 🎉🎉"
    else:
        user_count_message = f"They have been the fastest Pioneer {clicks} times and on a *{streak}* click streak!"

    if db.clicks_check_is_fastest(time_taken):
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
        callbacks.click_me,
        settings.BUTTON_TIME,
        chat_id=urls.TG_MAIN_CHANNEL_ID,
        name="Click Me",
    )


async def clicks_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if tools.is_admin(update.effective_user.id):
        try:
            result_text = db.clicks_reset()
            await query.edit_message_text(text=result_text)
        except Exception as e:
            await query.answer(
                text=f"An error occurred: {str(e)}", show_alert=True
            )
    else:
        await query.answer(text="Admin only.", show_alert=True)
        return


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


async def liquidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    existing_wallet = db.wallet_get(user_id)

    if not existing_wallet:
        await query.answer(
            "You have not registered a wallet. Please use /register in private.",
            show_alert=True,
        )
        return

    try:
        _, loan_id, chain = query.data.split(":")
        chain_info, _ = chains.get_info(chain)

        message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Liquidating loan {loan_id} ({chain_info.name}), Please wait...",
        )

        result = await onchain.liquidate_loan(int(loan_id), chain, user_id)

        if result.startswith("Error"):
            await query.answer(result, show_alert=True)
            return

        await message.delete()
        await query.edit_message_caption(caption=result, reply_markup=None)

    except Exception as e:
        await message.delete()
        await query.answer(
            f"Error during liquidation: {str(e)}", show_alert=True
        )


async def pushall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    existing_wallet = db.wallet_get(user_id)

    if not existing_wallet:
        await query.answer(
            "You have not registered a wallet. Please use /register in private.",
            show_alert=True,
        )
        return

    _, token, chain = query.data.split(":")
    chain_info, _ = chains.get_info(chain)

    config = await splitters.get_push_settings(chain, token)
    address = config["address"]
    abi = config["abi"]
    name = config["name"]
    threshold = config["threshold"]
    contract_type = config["contract_type"]

    contract = chain_info.w3.eth.contract(
        address=chain_info.w3.to_checksum_address(address), abi=abi
    )

    available_tokens = config["calculate_tokens"](contract)

    if float(available_tokens) < float(threshold):
        await query.answer(
            f"{chain_info.name} {name} balance to low to push.",
            show_alert=True,
        )
        return

    try:
        message = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Pushing {contract_type} ({chain_info.name}), Please wait...",
        )

        if contract_type == "hub":
            token_address = config["token_address"]
            result = await onchain.splitter_push(
                contract_type, address, abi, chain, user_id, token_address
            )
        else:
            result = await onchain.splitter_push(
                contract_type, address, abi, chain, user_id
            )

        if result.startswith("Error"):
            await query.answer(result, show_alert=True)
            return

        await message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=result
        )
    except Exception as e:
        await message.delete()
        await query.answer(
            f"Error during {name} push: {str(e)}", show_alert=True
        )


async def settings_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if tools.is_admin(query.from_user.id):
        callback_data = query.data

        setting = callback_data.replace("settings_toggle_", "")

        try:
            current_status = db.settings_get(setting)
            new_status = not current_status
            db.settings_set(setting, new_status)

            formatted_setting = setting.replace("_", " ").title()
            await query.answer(
                text=f"{formatted_setting} turned {'ON' if new_status else 'OFF'}."
            )

            settings = db.settings_get_all()
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


async def stuck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, chain = query.data.split(":")
    user_id = query.from_user.id

    try:
        result_text = await onchain.stuck_tx(chain, user_id)

        await query.edit_message_text(text=result_text)
    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}", show_alert=True
        )


async def wallet_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        result_text = db.wallet_remove(user_id)

        await query.edit_message_text(text=result_text)
    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}", show_alert=True
        )


async def welcome_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    action, allowed_user_id = query.data.split(":")

    if action == "unmute" and str(user_id) == allowed_user_id:
        user_restrictions = {key: True for key in auto.welcome_rescrictions}

        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=user_restrictions,
        )
        try:
            previous_welcome_message_id = context.bot_data.get(
                "welcome_message_id"
            )
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=previous_welcome_message_id,
            )
        except Exception:
            pass


HANDLERS = [
    (cancel, r"^cancel$"),
    (click_me, r"^click_button:\d+$"),
    (clicks_reset, r"^clicks_reset$"),
    (confirm, r"^question:.*"),
    (liquidate, r"^liquidate:\d+:[a-z]+$"),
    (
        pushall,
        r"^push:(eco|treasury|x7r|x7dao|x710[1-5]):[a-z]+$",
    ),
    (settings_toggle, r"^settings_toggle_"),
    (stuck, r"^stuck:.*$"),
    (wallet_remove, r"^wallet_remove$"),
    (welcome_button, r"unmute:.+"),
]
