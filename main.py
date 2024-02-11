import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler, MessageHandler, filters

import bot

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app = (ApplicationBuilder()
           .token(os.environ['TELEGRAM_BOT_TOKEN'])
           .build())

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", bot.start),
                      CommandHandler("cancel", bot.cancel),
                      CommandHandler("delete", bot.delete),
                      CommandHandler("highlights", bot.cmd_highlight_sending),
                      CommandHandler("help", bot.help)
                      ],
        states={
            bot.OMNIVORE_TOKEN_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.omnivore_token)],
            bot.OMNIVORE_LABEL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.omnivore_label)],
            bot.OMNIVORE_HIGHLIGHTS_AMOUNT_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.highlights_amount)],
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)],
    )

    app.add_handler(conv_handler)

    logging.info('Bot starting...')

    app.run_polling(allowed_updates=Update.ALL_TYPES)
