from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Message
from telegram.ext import Updater, MessageHandler, CommandHandler, ConversationHandler, Filters, CallbackContext
from Tester import TESTER
from time import sleep
from User import USERS

TOKEN = '2128072171:AAES8w5dOuYV5e-0TbRq8h7Y6pV1KntEvDg'
ALIAS = range(1)

class BotTelegram:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dispatcher = self.updater.dispatcher

        entry_points = [
            CommandHandler('start',self.start)
        ]
        states = {
            ALIAS: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command & Filters.regex("^([a-zA-Z]){3,15}$"),
                    callback=self.register
                )
            ]
        }
        fallbacks = [
            MessageHandler(filters=Filters.all, callback=self.fallbackCallback)
        ]

        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('state', self.state))

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.diffusion))

    def run(self):
        self.updater.start_polling()
        #self.updater.idle()

    def stop(self):
        self.updater.stop()

    def state(self, update: Update, context: CallbackContext) -> None:
        Message.delete(update.message)
        state = TESTER.test()['msg']
        resp = update.message.reply_text(state)
        sleep(60)
        Message.delete(resp)

    def start(self, update: Update, context: CallbackContext) -> None:
        new_id = update.message.chat.id

        if USERS.is_registered(new_id):
            user = USERS.get_user(new_id)
            update.message.reply_text(f"Hi {user.alias}!")
            self.help(update)
            return ConversationHandler.END
        else:
            update.message.reply_text("Welcome!")
            update.message.reply_text("I'm @TheGodOfTradingBot")
            update.message.reply_text('Enter your name')
            return ALIAS

    def help(self, update: Update) -> None:
        Message.delete(update.message)
        buttons = [[
            KeyboardButton('/state'),
            KeyboardButton('/help')
        ]]

        keyboardMarkup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        msg = 'Comandos'
        update.message.reply_text(msg, reply_markup=keyboardMarkup)

    def notify(self, msg):
        for id in USERS.get_IDs():
            self.updater.bot.send_message(id, msg)

    def diffusion(self, update: Update, context: CallbackContext) -> None:
        user = USERS.get_user(update.message.chat.id)
        if user.is_god():
            for user_id in USERS.get_IDs():
                if user_id != user.id:
                    self.updater.bot.send_message(user_id, update.message.text)

    def register(self, update, callback):
        new_id = update.message.chat.id
        alias = update.message.text
        USERS.register(new_id, alias)
        update.message.reply_text('You have been registered')
        self.help(update)
        return ConversationHandler.END

    def fallbackCallback(self, update, callback):
        update.message.reply_text('The name entered is invalid. Remember that it must be between 3 and 15 characters. It cannot contain spaces, symbols, or numbers.')


TELEGRAM = BotTelegram()
