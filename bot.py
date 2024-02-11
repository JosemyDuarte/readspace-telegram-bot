import os

from telegram import Update, ReplyKeyboardRemove, ForceReply
from telegram.ext import ContextTypes, ConversationHandler

from highlight_sender import HighlightSender
from omnivore import OmnivoreQLClient
from users import UserDatabase

OMNIVORE_TOKEN_STATE, OMNIVORE_LABEL_STATE, OMNIVORE_HIGHLIGHTS_AMOUNT_STATE = range(3)

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
usersDb = UserDatabase(spreadsheet_id=os.environ['SPREADSHEET_ID'], gcp_credentials=os.environ['GCP_CREDENTIALS'])
highlightSender = HighlightSender(telegram_bot_token=TELEGRAM_BOT_TOKEN)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = usersDb.get_user(str(update.message.from_user.id))
    if user is None:
        await update.message.reply_text(f'Hello {update.effective_user.first_name}! '
                                        f'Please enter your Omnivore API token:',
                                        reply_markup=ForceReply()
                                        )
        return OMNIVORE_TOKEN_STATE
    else:
        await update.message.reply_text(f'Hi: {update.message.from_user.first_name}!\n'
                                        f'You have already registered.\n\n'
                                        f'If you want to delete your data, please run /delete command.',
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def omnivore_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    otoken = update.message.text

    omnivore_client = OmnivoreQLClient(otoken)
    omnivore_profile = omnivore_client.get_profile()
    if len(omnivore_profile) == 0:
        await update.message.reply_text(
            f'Invalid Omnivore API token. Please try again with a valid token running /start command one more time.')
        return ConversationHandler.END

    context.user_data['omnivore_token'] = otoken

    await update.message.reply_text(f'Please enter the label name you want to filter by:',
                                    reply_markup=ForceReply()
                                    )

    return OMNIVORE_LABEL_STATE


async def omnivore_label(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['label_name'] = update.message.text

    await update.message.reply_text(f'Please enter the number of random highlights you would like to receive [1, 10]:',
                                    reply_markup=ForceReply()
                                    )

    return OMNIVORE_HIGHLIGHTS_AMOUNT_STATE


async def highlights_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = int(update.message.text)
        if amount < 1 or amount > 10:
            raise ValueError
    except ValueError:
        await update.message.reply_text(f'Invalid number. Please try starting again with /start command.')
        return ConversationHandler.END

    label_name = context.user_data['label_name']
    otoken = context.user_data['omnivore_token']
    context.user_data['amount'] = update.message.text

    usersDb.save_user(chat_id=str(update.message.from_user.id),
                      first_name=update.message.from_user.first_name,
                      token=otoken,
                      label=label_name,
                      amount=amount,
                      )

    await update.message.reply_text(f'Here is your summary:\n'
                                    f'First Name: {update.message.from_user.first_name}\n'
                                    f'Label: {label_name}\n'
                                    f'Omnivore Token: {otoken}\n'
                                    f'Amount: {amount}\n\n'
                                    f'Wait a moment while we retrieve your highlights...\n',
                                    )

    return await send_highlights(int(amount), label_name, otoken, update)


# Command handler for highlights
async def cmd_highlight_sending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = usersDb.get_user(str(update.message.from_user.id))
    if user is None:
        await update.message.reply_text(f'Hi: {update.message.from_user.first_name}!\n'
                                        f'You have not registered yet.\n\n'
                                        f'If you want to start, please run /start command.',
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    return await send_highlights(int(user.amount.value), user.label.value, user.token.value, update)


async def send_highlights(amount: int, label_name: str, otoken: str, update: Update):
    sent = await highlightSender.send_highlights(chat_id=str(update.message.from_user.id),
                                                 token=otoken,
                                                 label=label_name,
                                                 amount=int(amount))
    if not sent:
        await update.message.reply_text(f'Currently there are no highlights found for the label: <b>{label_name}</b>.\n'
                                        f'Whenever there are highlights, we will send them to you.\n\n',
                                        reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return ConversationHandler.END


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deleted = usersDb.delete_user(str(update.message.from_user.id))

    if deleted:
        await update.message.reply_text(f'Hi: {update.message.from_user.first_name}!\n'
                                        f'We have deleted your data from our database.\n\n'
                                        f'If you want to start again, please run /start command.',
                                        reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(f'Hi: {update.message.from_user.first_name}!\n'
                                        f'You have not registered yet.\n\n'
                                        f'If you want to start, please run /start command.',
                                        reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hi: {update.message.from_user.first_name}!\n'
                                    f'You can use the following commands:\n\n'
                                    f'/start - Start the registration process\n'
                                    f'/delete - Delete your data from our database\n'
                                    f'/highlights - Send your highlights\n'
                                    f'/help - Show this help',
                                    reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
