from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
import threading

TOKEN = '2128072171:AAEjPPOqS_ICrRJ2HudLNgBgsqhI6HtdRnI'
CHAT_ID = [2004536384, 1369437188]


class BotTelegram:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler('state', self.state))
        self.dispatcher.add_handler(CommandHandler('stadistics', self.stadistics))
        self.dispatcher.add_handler(CommandHandler('help', self.help))

    def start(self):
        self.updater.start_polling()
        #self.updater.idle()

    def echo(self, update: Update, context: CallbackContext) -> None:
        """Echo the user message."""
        print(update.message.chat.id)
        update.message.reply_text(update.message.text)

    def state(self, update: Update, context: CallbackContext) -> None:
        state = TESTER.test()
        update.message.reply_text(state)

    def help(self, update: Update, context: CallbackContext) -> None:
        comands = 'Comands:\n /state\n /help'
        update.message.reply_text(comands)

    def notify(self, msg):
        for id in CHAT_ID:
            self.updater.bot.send_message(id, msg)

    def stadistics(self):
        pass


TELEGRAM = BotTelegram()
