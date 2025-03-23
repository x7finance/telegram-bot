from telegram.ext import (
    ChatMemberHandler,
    MessageHandler,
    filters,
)

from bot.callbacks import clickme, general, protocol, reminders, welcome

HANDLERS = [
    (clickme.click, r"^click_button:\d+$"),
    (clickme.reset, r"^clicks_reset$"),
    (general.cancel, r"^cancel$"),
    (general.confirm, r"^question:.*"),
    (general.settings_toggle, r"^settings_toggle_"),
    (general.wallet_remove, r"^wallet_remove$"),
    (protocol.liquidate, r"^liquidate:\d+:[a-z]+$"),
    (
        protocol.pushall,
        r"^push:(eco|treasury|x7r|x7dao|x710[1-5]):[a-z]+$",
    ),
    (protocol.stuck_tx, r"^stuck:.*$"),
    (reminders.remove, r"^reminder_remove:\d+$"),
    (reminders.set, r"^reminder:.*"),
    (welcome.button, r"^unmute:\d+$"),
]

AUTO_HANDLERS = [
    ChatMemberHandler(welcome.message, ChatMemberHandler.CHAT_MEMBER),
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS
        | filters.StatusUpdate.LEFT_CHAT_MEMBER,
        welcome.delete,
    ),
    MessageHandler(filters.TEXT & ~filters.COMMAND, general.auto_replies),
]
