from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Message
from telegram.ext import Updater, MessageHandler, CommandHandler, ConversationHandler, Filters, CallbackContext
from Tester import TESTER
from time import sleep
from User import USERS
from Trader import get_results, get_trades
from Binance import WS
from Config import THREADS
from threading import Thread

TOKEN = '2128072171:AAES8w5dOuYV5e-0TbRq8h7Y6pV1KntEvDg'
ALIAS = 0
MSG = 0

class BotTelegram:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dispatcher = self.updater.dispatcher

        ###REGISTER CONVERSATION###
        entry_points = [CommandHandler('start',self.start)]
        states = {
            ALIAS: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command & Filters.regex("^([a-zA-Z]){3,15}$"),
                    callback=self.register
                )
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallbackRegisterCallback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END REGISTER CONVERSATION####

        ###DIFFUSION CONVERSATION###
        entry_points = [CommandHandler('diffusion', self.diffusion)]
        states = {
            MSG: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=self._diffusion
                )
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallbackDiffusionCallback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END DIFFUSION CONVERSATION###

        ###COMMANDS###
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('state', self.state))
        self.dispatcher.add_handler(CommandHandler('results', self.results))
        self.dispatcher.add_handler(CommandHandler('trades', self.trades))
        self.dispatcher.add_handler(CommandHandler('turnOn', self.turn_on))
        self.dispatcher.add_handler(CommandHandler('turnOff', self.turn_off))
        self.dispatcher.add_handler(CommandHandler('reset', self.reset))
        self.dispatcher.add_handler(CommandHandler('allBuy', self.all_buy))
        self.dispatcher.add_handler(CommandHandler('allSell', self.all_sell))
        ###END COMMANDS###

        ###MESSAGES###
        ###END MESSAGES###

    def run(self):
        self.updater.start_polling()
        #self.updater.idle()

    def stop(self):
        self.updater.stop()

    def state(self, update: Update, context: CallbackContext) -> None:
        Message.delete(update.message)
        state = TESTER.test()['msg']
        resp = update.message.reply_text(state)
        Thread(target=self.clean, args=(resp, 10)).start()

    def start(self, update: Update, context: CallbackContext) -> int:
        new_id = update.message.chat.id

        if USERS.is_registered(new_id):
            user = USERS.get_user(new_id)
            update.message.reply_text(f"Hi {user.alias}!")
            self.help(update, context)
            return ConversationHandler.END
        else:
            update.message.reply_text("Welcome!")
            update.message.reply_text("I'm @TheGodOfTradingBot")
            update.message.reply_text('Enter your name')
            return ALIAS

    def help(self, update: Update, context: CallbackContext) -> None:
        Message.delete(update.message)
        buttons = [
            [
                KeyboardButton('/state'),
            ],
            [
                KeyboardButton('/trades'),
                KeyboardButton('/results')
            ],
            [
                KeyboardButton('/turnOn'),
                KeyboardButton('/turnOff'),
                KeyboardButton('/reset')
            ],
            [
                KeyboardButton('/diffusion'),
                KeyboardButton('/help')
            ]
        ]

        keyboardMarkup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        msg = 'Comandos'
        update.message.reply_text(msg, reply_markup=keyboardMarkup)

    def notify(self, msg):
        for id in USERS.get_IDs():
            self.updater.bot.send_message(id, msg)

    def diffusion(self, update: Update, context: CallbackContext) -> int:
        user = USERS.get_user(update.message.chat.id)
        if user.is_god():
            update.message.reply_text('What message do you want to spread?\nEnter /cancel to exit')
            return MSG
        else:
            update.message.reply_text('You do not have permission to diffusion')
            return ConversationHandler.END

    def _diffusion(self, update: Update, context: CallbackContext) -> None:
        user = USERS.get_user(update.message.chat.id)
        for user_id in USERS.get_IDs():
            if user_id != user.id:
                self.updater.bot.send_message(user_id, update.message.text)
        update.message.reply_text('Message sent')
        return ConversationHandler.END

    def register(self, update, callback):
        new_id = update.message.chat.id
        alias = update.message.text
        USERS.register(new_id, alias)
        update.message.reply_text('You have been registered')
        self.help(update, callback)
        return ConversationHandler.END

    def results(self, update: Update, context: CallbackContext) -> None:
        Message.delete(update.message)
        results = get_results()
        msg = ''
        for result in results:
            msg += result
        resp = update.message.reply_text(msg)
        Thread(target=self.clean, args=(resp, 60)).start()

    def trades(self, update: Update, context: CallbackContext) -> None:
        Message.delete(update.message)
        path = get_trades()
        resp = update.message.reply_document(document=open(path))
        Thread(target=self.clean, args=(resp, 60)).start()

    def turn_on(self, update: Update, context: CallbackContext) -> None:
        user = USERS.get_user(update.message.chat.id)
        if user.is_god():
            Message.delete(update.message)
            WS.start()
            update.message.reply_text('On')
        else:
            update.message.reply_text("You don't have permission to perform this action")

    def turn_off(self, update: Update, context: CallbackContext) -> None:
        user = USERS.get_user(update.message.chat.id)
        if user.is_god():
            Message.delete(update.message)
            WS.stop()
            update.message.reply_text('Off')
        else:
            update.message.reply_text("You don't have permission to perform this action")

    def reset(self, update: Update, context: CallbackContext) -> None:
        user = USERS.get_user(update.message.chat.id)
        if user.is_god():
            Message.delete(update.message)
            update.message.reply_text('Restarting...')
            WS.restart()
            update.message.reply_text('On')
        else:
            update.message.reply_text("You don't have permission to perform this action")

    def all_buy(self, update: Update, context: CallbackContext) -> None:
        pass

    def all_sell(self, update: Update, context: CallbackContext) -> None:
        pass

    def clean(self, msg, t=60):
        sleep(t)
        Message.delete(msg)

    def fallbackRegisterCallback(self, update, callback):
        update.message.reply_text('The name entered is invalid. Remember that it must be between 3 and 15 characters. It cannot contain spaces, symbols, or numbers.')

    def fallbackDiffusionCallback(self, update, callback):
        msg = update.message.text
        if msg == '/cancel':
            update.message.reply_text('Diffusion canceled')
            return ConversationHandler.END
        else:
            update.message.reply_text('You cannot transmit this message, please enter a different one\nEnter /cancel to exit')

TELEGRAM = BotTelegram()
