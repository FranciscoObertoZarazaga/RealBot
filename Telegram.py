from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Message
from telegram.ext import Updater, MessageHandler, CommandHandler, ConversationHandler, Filters, CallbackContext
from Tester import TESTER
from time import sleep
from User import USERS
from Trader import get_results, get_trades
import Bot
from Trader import TRADERS
from threading import Thread
from tools.singleton import singleton

TOKEN = '2128072171:AAES8w5dOuYV5e-0TbRq8h7Y6pV1KntEvDg'
ALIAS = 0
MSG = 0
CONFIRM = 0


@singleton
class BotTelegram:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dispatcher = self.updater.dispatcher

        ###REGISTER CONVERSATION###
        entry_points = [CommandHandler('start', self.start)]
        states = {
            ALIAS: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command & Filters.regex("^([a-zA-Z]){3,15}$"),
                    callback=self.register
                )
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallback_register_callback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END REGISTER CONVERSATION####

        ###DIFFUSION CONVERSATION###
        entry_points = [CommandHandler('diffusion', self.diffusion)]
        states = {
            MSG: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=self._diffusion
                ),
                CommandHandler('cancel', self.cancel)
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallback_diffusion_callback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END DIFFUSION CONVERSATION###

        ###ALL_BUY CONVERSATION###
        entry_points = [CommandHandler('allBuy', self.confirm)]
        states = {
            CONFIRM: [
                CommandHandler('confirm', self.all_buy),
                CommandHandler('cancel', self.cancel)
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallback_transaction_callback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END ALL_BUY CONVERSATION###

        ###ALL_SELL CONVERSATION###
        entry_points = [CommandHandler('allSell', self.confirm)]
        states = {
            CONFIRM: [
                CommandHandler('confirm', self.all_sell),
                CommandHandler('cancel', self.cancel)
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallback_transaction_callback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END ALL_SELL CONVERSATION###

        ###COMMANDS###
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('state', self.state))
        self.dispatcher.add_handler(CommandHandler('results', self.results))
        self.dispatcher.add_handler(CommandHandler('trades', self.trades))
        self.dispatcher.add_handler(CommandHandler('turnOn', self.turn_on))
        self.dispatcher.add_handler(CommandHandler('turnOff', self.turn_off))
        self.dispatcher.add_handler(CommandHandler('reset', self.reset))
        ###END COMMANDS###

        ###MESSAGES###
        ###END MESSAGES###

    def run(self):
        self.updater.start_polling()
        # self.updater.idle()

    def stop(self):
        self.updater.stop()

    def state(self, update: Update, _):
        Message.delete(update.message)
        state = TESTER.test()['msg']
        resp = update.message.reply_text(state)
        Thread(target=self.clean, args=(resp, 10)).start()

    def start(self, update: Update, context: CallbackContext):
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

    @staticmethod
    def help(update: Update, _):
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
                KeyboardButton('/allBuy'),
                KeyboardButton('/allSell')
            ],
            [
                KeyboardButton('/diffusion'),
                KeyboardButton('/help')
            ]
        ]

        keyboard_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        msg = 'Comandos'
        update.message.reply_text(msg, reply_markup=keyboard_markup)

    def notify(self, msg):
        for user_id in USERS.get_i_ds():
            self.updater.bot.send_message(user_id, msg)

    def diffusion(self, update: Update, _):
        if self.verify(update):
            update.message.reply_text('What message do you want to spread?\nEnter /cancel to exit')
            return MSG
        else:
            return ConversationHandler.END

    def _diffusion(self, update: Update, _):
        user = USERS.get_user(update.message.chat.id)
        for user_id in USERS.get_i_ds():
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

    def results(self, update: Update, _):
        Message.delete(update.message)
        results = get_results()
        msg = ''
        for result in results:
            msg += result
        resp = update.message.reply_text(msg)
        Thread(target=self.clean, args=(resp, 60)).start()

    def trades(self, update: Update, _):
        Message.delete(update.message)
        path = get_trades()
        resp = update.message.reply_document(document=open(path))
        Thread(target=self.clean, args=(resp, 60)).start()

    def turn_on(self, update: Update, _):
        if self.verify(update):
            Message.delete(update.message)
            Bot.BOT.start()
            update.message.reply_text('On')

    def turn_off(self, update: Update, _):
        if self.verify(update):
            Message.delete(update.message)
            Bot.BOT.stop()
            update.message.reply_text('Off')

    def reset(self, update: Update, _):
        if self.verify(update):
            Message.delete(update.message)
            update.message.reply_text('Restarting...')
            Bot.BOT.restart()
            update.message.reply_text('On')

    @staticmethod
    def all_buy(update: Update, _):
        buy_threads = list()
        for trader in TRADERS:
            buy_threads.append(Thread(target=trader.buy))
        for thread in buy_threads:
            thread.start()

        update.message.reply_text('All traders bought')
        return ConversationHandler.END

    @staticmethod
    def all_sell(update: Update, _):
        sell_threads = list()
        for trader in TRADERS:
            sell_threads.append(Thread(target=trader.sell()))
        for thread in sell_threads:
            thread.start()

        update.message.reply_text('All traders sold')
        return ConversationHandler.END

    @staticmethod
    def clean(msg, t=60):
        sleep(t)
        Message.delete(msg)

    def confirm(self, update: Update, _):
        if self.verify(update):
            update.message.reply_text('Enter /confirm to perform the action')
            update.message.reply_text('Enter /cancel to abort')
            return CONFIRM
        else:
            return ConversationHandler.END

    @staticmethod
    def verify(update):
        user = USERS.get_user(update.message.chat.id)
        is_god = user.is_god()
        if not is_god:
            update.message.reply_text("You don't have permission to perform this action")
        return is_god

    @staticmethod
    def cancel(update, _):
        update.message.reply_text('Canceled')
        return ConversationHandler.END

    @staticmethod
    def fallback_register_callback(update, _):
        update.message.reply_text(
            'The name entered is invalid. Remember that it must be between 3 and 15 characters. It cannot contain spaces, symbols, or numbers.')

    @staticmethod
    def fallback_diffusion_callback(update, _):
        update.message.reply_text(
            'You cannot transmit this message, please enter a different one\nEnter /cancel to exit')

    @staticmethod
    def fallback_transaction_callback(update, _):
        update.message.reply_text('error')


TELEGRAM = BotTelegram()
