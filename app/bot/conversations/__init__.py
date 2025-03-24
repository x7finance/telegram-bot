from telegram.ext import CallbackQueryHandler, filters, MessageHandler

from bot.conversations import general, reminders, withdraw, x7d


HANDLERS = [
    {
        "entry_points": [
            CallbackQueryHandler(withdraw.start, pattern="^withdraw:.*$")
        ],
        "states": {
            withdraw.TOKEN: [
                CallbackQueryHandler(withdraw.token, pattern="^withdraw:.*$")
            ],
            withdraw.AMOUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, withdraw.amount
                )
            ],
            withdraw.ADDRESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, withdraw.address
                )
            ],
            withdraw.CONFIRM: [
                CallbackQueryHandler(general.confirm, pattern="^withdraw:.*$")
            ],
        },
    },
    {
        "entry_points": [
            CallbackQueryHandler(x7d.start, pattern="^(mint|redeem):.*$")
        ],
        "states": {
            x7d.AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, x7d.amount)
            ],
            x7d.CONFIRM: [
                CallbackQueryHandler(
                    general.confirm, pattern="^(mint|redeem):.*$"
                )
            ],
        },
    },
    {
        "entry_points": [
            CallbackQueryHandler(
                reminders.start, pattern="^reminder:manual.*$"
            )
        ],
        "states": {
            reminders.DATE: [CallbackQueryHandler(reminders.date)],
            reminders.TIME: [CallbackQueryHandler(reminders.time)],
            reminders.MESSAGE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, reminders.message
                )
            ],
        },
    },
]
