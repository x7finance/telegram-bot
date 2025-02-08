from telegram import (
    ChatMember,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

import random, time
from typing import Optional, Tuple

from media import stickers, videos

from hooks import db, tools
from constants import text, urls

welcome_rescrictions = {
    "can_send_messages": False,
    "can_send_media_messages": False,
    "can_send_other_messages": False,
    "can_add_web_page_previews": False,
}


async def button_send(context: ContextTypes.DEFAULT_TYPE):
    if not db.settings_get("click_me"):
        return
    context.bot_data["first_user_clicked"] = False

    previous_click_me_id = context.bot_data.get("click_me_id")
    previous_clicked_id = context.bot_data.get("clicked_id")

    if previous_click_me_id:
        try:
            await context.bot.delete_message(
                chat_id=urls.TG_MAIN_CHANNEL_ID, message_id=previous_click_me_id
            )
            await context.bot.delete_message(
                chat_id=urls.TG_MAIN_CHANNEL_ID, message_id=previous_clicked_id
            )
        except Exception:
            pass

    current_button_data = str(random.randint(1, 100000000))
    context.bot_data["current_button_data"] = f"click_button:{current_button_data}"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Click Me!", callback_data=context.bot_data["current_button_data"]
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


async def replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def welcome_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.effective_message.id
        )
    except Exception:
        return


async def welcome_member(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None)
    )

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_id = update.effective_chat.id
    result = await welcome_member(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    new_member = update.chat_member.new_chat_member

    if str(channel_id) == urls.TG_MAIN_CHANNEL_ID:
        new_member_id = new_member.user.id

        new_member_username = (
            f"@{new_member.user.username}"
            if new_member.user.username
            else f"{new_member.user.first_name} {new_member.user.last_name or ''}".strip()
        )

        welcome_message = None
        reply_markup = None

        if not was_member and is_member:
            previous_welcome_message_id = context.bot_data.get("welcome_message_id")
            if previous_welcome_message_id:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=previous_welcome_message_id,
                    )
                except Exception:
                    pass

            if db.settings_get("welcome_restrictions"):
                await context.bot.restrict_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=new_member_id,
                    permissions=welcome_rescrictions,
                )
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="❗ I am human! ❗",
                                callback_data=f"unmute:{new_member_id}",
                            )
                        ]
                    ]
                )

            welcome_message = await update.effective_chat.send_video(
                video=open(videos.WELCOMEVIDEO, "rb"),
                caption=f"{text.welcome(new_member_username)}",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

        if welcome_message:
            context.bot_data["welcome_message_id"] = welcome_message.message_id
