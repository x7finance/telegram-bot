from telegram import *
from telegram.ext import *

import os, time
from datetime import datetime

from bot import auto, callbacks
from constants import ca, chains, settings, urls
from hooks import  api, db, functions, tools
from main import application

job_queue = application.job_queue
etherscan = api.Etherscan()


async def admin_toggle(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    callback_data = query.data
    if not callback_data.startswith("admin_toggle_"):
        return

    setting = callback_data.replace("admin_toggle_", "")

    try:
        current_status = db.settings_get(setting)
        new_status = not current_status
        db.settings_set(setting, new_status)

        formatted_setting = setting.replace("_", " ").title()
        await query.answer(
            text=f"{formatted_setting} updated to {'ON' if new_status else 'OFF'}."
        )

        settings = db.settings_get_all()
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{s.replace('_', ' ').title()}: {'ON' if v else 'OFF'}",
                    callback_data=f"admin_toggle_{s}"
                )
            ]
            for s, v in settings.items()
        ]
        keyboard.append(
            [
                InlineKeyboardButton("Reset Clicks", callback_data="clicks_reset_start")
            ]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Bot Settings", reply_markup=reply_markup)

    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}",
            show_alert=True
        )


async def click_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button_click_timestamp = time.time()

    current_button_data = context.bot_data.get("current_button_data")
    if not current_button_data or update.callback_query.data != current_button_data:
        return

    button_generation_timestamp = context.bot_data.get("button_generation_timestamp")
    if not button_generation_timestamp:
        await update.callback_query.answer("Too slow!", show_alert=True)
        return

    button_data = update.callback_query.data
    user = update.effective_user
    user_info = user.username or f"{user.first_name} {user.last_name}" or user.first_name

    context.user_data.setdefault("clicked_buttons", set())
    if button_data in context.user_data["clicked_buttons"]:
        await update.callback_query.answer("You have already clicked this button.", show_alert=True)
        return

    context.user_data["clicked_buttons"].add(button_data)

    if button_data == current_button_data:
        time_taken = button_click_timestamp - button_generation_timestamp

        await db.clicks_update(user_info, time_taken)

        if not context.bot_data.get("first_user_clicked"):
            context.bot_data["first_user_clicked"] = True

            user_data = db.clicks_get_by_name(user_info)
            clicks = user_data[0]
            streak = user_data[2]
            total_click_count = db.clicks_get_total()

            if clicks == 1:
                click_message = "🎉🎉 This is their first button click! 🎉🎉"
            elif clicks % 10 == 0:
                click_message = f"🎉🎉 They have been the fastest Pioneer {clicks} times and on a *{streak}* click streak! 🎉🎉"
            else:
                click_message = f"They have been the fastest Pioneer {clicks} times and on a *{streak}* click streak!"

            if db.clicks_check_is_fastest(time_taken):
                click_message += f"\n\n🎉🎉 {time_taken:.3f} seconds is the new fastest time! 🎉🎉"

            if db.settings_get('burn'):
                clicks_needed = settings.CLICK_ME_BURN - (total_click_count % settings.CLICK_ME_BURN)
                message_text = (
                    f"{tools.escape_markdown(user_info)} was the fastest Pioneer in {time_taken:.3f} seconds!\n\n"
                    f"{click_message}\n\n"
                    f"The button has been clicked a total of {total_click_count} times by all Pioneers!\n\n"
                    f"Clicks till next X7R Burn: *{clicks_needed}*\n\n"
                    f"use `/leaderboard` to see the fastest Pioneers!\n\n"
                )
            else:
                message_text = (
                    f"{tools.escape_markdown(user_info)} was the fastest Pioneer in {time_taken:.3f} seconds!\n\n"
                    f"{click_message}\n\n"
                    f"The button has been clicked a total of {total_click_count} times by all Pioneers!\n\n"
                    f"use `/leaderboard` to see the fastest Pioneers!\n\n"
                )

            photos = await context.bot.get_user_profile_photos(update.effective_user.id, limit=1)
            if photos and photos.photos and photos.photos[0]:
                photo = photos.photos[0][0].file_id
                clicked = await context.bot.send_photo(
                    photo=photo,
                    chat_id=update.effective_chat.id,
                    caption=message_text,
                    parse_mode="Markdown"
                )
            else:
                clicked = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message_text,
                    parse_mode="Markdown"
                )

            if db.settings_get('burn') and total_click_count % settings.CLICK_ME_BURN == 0:
                burn_message = await functions.burn_x7r(settings.burn_amount(), "eth")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"🔥🔥🔥🔥🔥🔥🔥🔥\n\nThe button has been clicked a total of {total_click_count} times by all Pioneers!\n\n{burn_message}"
                )

            context.bot_data['clicked_id'] = clicked.message_id

            settings.RESTART_TIME = datetime.now().timestamp()
            settings.BUTTON_TIME = settings.random_button_time()
            job_queue.run_once(
                callbacks.click_me,
                settings.BUTTON_TIME,
                chat_id=urls.TG_MAIN_CHANNEL_ID,
                name="Click Me",
            )


async def clicks_reset(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="clicks_reset_yes"),
            InlineKeyboardButton("No", callback_data="clicks_reset_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Are you sure you want to reset clicks?",
        reply_markup=reply_markup
    )


async def clicks_reset_no(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(text="Admin only.", show_alert=True)
        return

    await query.edit_message_text(
        text="Action canceled. No changes were made."
    )


async def clicks_reset_yes(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != int(os.getenv("TELEGRAM_ADMIN_ID")):
        await query.answer(
            text="Admin only.",
            show_alert=True
        )
        return

    try:
        result_text = db.clicks_reset()
        await query.edit_message_text(
            text=f"Clicks have been reset. {result_text}"
        )
    except Exception as e:
        await query.answer(
            text=f"An error occurred: {str(e)}",
            show_alert=True
        )


async def liquidate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        _, chain, loan_id = query.data.split(":")
        
        result = functions.liquidate_loan(int(loan_id), chain)
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Liquidation successful: {result}"
        )

    except Exception as e:
        await query.answer(f"Error during liquidation: {str(e)}", show_alert=True)


async def pushall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    
    is_admin = user_id == int(os.getenv("TELEGRAM_ADMIN_ID"))
    if not is_admin:
        await query.answer("Admin only.", show_alert=True)
        return

    action, chain = query.data.split(":")
    chain_info, error_message = chains.get_info(chain)

    contract = None
    splitter_balance = 0
    token_address = None
    threshold = 0
    contract_type = None

    settings = {
        "push_eco": {
            "splitter_address": ca.ECO_SPLITTER(chain),
            "splitter_name": "Ecosystem Splitter",
            "threshold": 0.01,
            "contract_type": "splitter",
            "balance_func": lambda contract: contract.functions.outletBalance(4).call() / 10 ** 18
        },
        "push_treasury": {
            "splitter_address": ca.TREASURY_SPLITTER(chain),
            "splitter_name": "Treasury Splitter",
            "threshold": 0.01,
            "contract_type": "splitter",
            "balance_func": lambda _: etherscan.get_native_balance(ca.TREASURY_SPLITTER(chain), chain)
        },
        "push_x7r": {
            "splitter_address": ca.X7R_LIQ_HUB(chain),
            "splitter_name": "X7R Liquidity Hub",
            "token_address": ca.X7R(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda contract: etherscan.get_token_balance(
                ca.X7R_LIQ_HUB(chain), ca.X7R(chain), chain
            ) - (contract.functions.x7rLiquidityBalance().call() / 10 ** 18)
        },
        "push_x7dao": {
            "splitter_address": ca.X7DAO_LIQ_HUB(chain),
            "splitter_name": "X7DAO Liquidity Hub",
            "token_address": ca.X7DAO(chain),
            "threshold": 10000,
            "contract_type": "hub",
            "balance_func": lambda contract: etherscan.get_token_balance(
                ca.X7DAO_LIQ_HUB(chain), ca.X7DAO(chain), chain
            ) - (contract.functions.x7daoLiquidityBalance().call() / 10 ** 18)
        },
    }

    if action not in settings:
        await query.answer("Invalid action.", show_alert=True)
        return

    config = settings[action]
    splitter_address = config["splitter_address"]
    splitter_name = config["splitter_name"]
    threshold = config["threshold"]
    contract_type = config["contract_type"]
    token_address = config.get("token_address")

    if contract_type in ["splitter", "hub"]:
        contract = chain_info.w3.eth.contract(
            address=chain_info.w3.to_checksum_address(splitter_address),
            abi=etherscan.get_abi(splitter_address, chain),
        )

    splitter_balance = config["balance_func"](contract)

    if splitter_balance < threshold:
        await query.answer(f"{chain_info.name} {splitter_name} has no balance to push.", show_alert=True)
        return

    try:
        if contract_type == "hub":
            result = functions.splitter_push(contract_type, splitter_address, chain, token_address)
        else:
            result = functions.splitter_push(contract_type, splitter_address, chain)

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=result
        )
    except Exception as e:
        await query.answer(f"Error during {splitter_name} push: {str(e)}", show_alert=True)


async def welcome_button(update: Update, context: CallbackContext) -> None:
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
            previous_welcome_message_id = context.bot_data.get('welcome_message_id')
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=previous_welcome_message_id
            )
        except Exception:
            pass