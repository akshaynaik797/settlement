from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters
import logging


updater = Updater(token='', use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot by aknaik")
    update.message.reply_text('sadasdas')
    updates = updater.get_updates()
    print([u.message.text for u in updates])

def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
caps_handler = CommandHandler('caps', caps)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(caps_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(unknown_handler)

if __name__ == '__main__':
    updater.start_polling()
    a = input('type stop to stop:')
    if 'stop' in a:
        updater.stop()
        exit()