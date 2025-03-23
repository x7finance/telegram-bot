from telegram import (
    ChatMember,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from constants.general import text, urls
from media import videos
from services import get_dbmanager

db = get_dbmanager()

RESTRICTIONS = {
    "can_send_messages": False,
    "can_send_media_messages": False,
    "can_send_other_messages": False,
    "can_add_web_page_previews": False,
}


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    action, allowed_user_id = query.data.split(":")

    if action == "unmute" and str(user_id) == allowed_user_id:
        user_restrictions = {key: True for key in RESTRICTIONS}

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
    else:
        await query.answer("This button is not for you!", show_alert=True)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.effective_message.id,
        )
    except Exception:
        return


async def member(chat_member_update: ChatMemberUpdated):
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


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.effective_chat.id
    result = await member(update.chat_member)
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
            welcome_caption = await text.welcome(new_member_username)

            previous_welcome_message_id = context.bot_data.get(
                "welcome_message_id"
            )
            if previous_welcome_message_id:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=previous_welcome_message_id,
                    )
                except Exception:
                    pass

            if await db.settings.get("welcome_restrictions"):
                await context.bot.restrict_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=new_member_id,
                    permissions=RESTRICTIONS,
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
                caption=welcome_caption,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

        if welcome_message:
            context.bot_data["welcome_message_id"] = welcome_message.message_id
