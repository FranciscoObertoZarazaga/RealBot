from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Message
from telegram.ext import Updater, MessageHandler, CommandHandler, ConversationHandler, Filters, CallbackContext
from Tester import TESTER
from time import sleep
import Bot
import Trader
from threading import Thread
from tools.singleton import singleton
from Config import TELEGRAM_ID
from telegram.error import NetworkError

TOKEN = '2128072171:AAES8w5dOuYV5e-0TbRq8h7Y6pV1KntEvDg'
ALIAS = 0
MSG = 0
CONFIRM = 0

@singleton
class BotTelegram:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dispatcher = self.updater.dispatcher

        ###BUY CONVERSATION###
        entry_points = [CommandHandler('buy', self.confirm)]
        states = {
            CONFIRM: [
                CommandHandler('confirm', self.buy),
                CommandHandler('cancel', self.cancel)
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallback_transaction_callback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END ALL_BUY CONVERSATION###

        ###ALL_SELL CONVERSATION###
        entry_points = [CommandHandler('sell', self.confirm)]
        states = {
            CONFIRM: [
                CommandHandler('confirm', self.sell),
                CommandHandler('cancel', self.cancel)
            ]
        }
        fallbacks = [MessageHandler(filters=Filters.all, callback=self.fallback_transaction_callback)]
        self.dispatcher.add_handler(ConversationHandler(entry_points, states, fallbacks))
        ###END ALL_SELL CONVERSATION###

        ###COMMANDS###
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('state', self.state))
        #self.dispatcher.add_handler(CommandHandler('results', self.results))
        #self.dispatcher.add_handler(CommandHandler('trades', self.trades))
        self.dispatcher.add_handler(CommandHandler('turnOn', self.turn_on))
        self.dispatcher.add_handler(CommandHandler('turnOff', self.turn_off))
        self.dispatcher.add_handler(CommandHandler('reset', self.reset))
        ###END COMMANDS###

        ###MESSAGES###
        ###END MESSAGES###

    def run(self):
        self.updater.start_polling()
        #self.updater.idle()

    def stop(self):
        self.updater.stop()

    def state(self, update: Update, _):
        Message.delete(update.message)
        state = TESTER.test()['msg']
        resp = update.message.reply_text(state)
        Thread(target=self.clean, args=(resp, 20)).start()

    def start(self, update: Update, context: CallbackContext):
        new_id = update.message.chat.id
        print('TELEGRAM_ID:', new_id)
        self.help(update, context)

    @staticmethod
    def help(update: Update, _):
        Message.delete(update.message)
        buttons = [
            [
                KeyboardButton('/state'),
            ],
            [
                KeyboardButton('/turnOn'),
                KeyboardButton('/turnOff'),
                KeyboardButton('/reset')
            ],
            [
                KeyboardButton('/buy'),
                KeyboardButton('/sell')
            ],
            [
                KeyboardButton('/help')
            ]
        ]

        keyboard_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        msg = 'Welcome'
        update.message.reply_text(msg, reply_markup=keyboard_markup)

    def notify(self, msg):
        self.updater.bot.send_message(TELEGRAM_ID, msg)

    '''def results(self, update: Update, _):
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
        Thread(target=self.clean, args=(resp, 60)).start()'''

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
    def buy(update: Update, _):
        Trader.TRADER.buy()
        update.message.reply_text('Buy: Done')
        return ConversationHandler.END

    @staticmethod
    def sell(update: Update, _):
        Trader.TRADER.sell()
        update.message.reply_text('Sell: Done')
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
        user_id = update.message.chat.id
        if user_id != TELEGRAM_ID:
            update.message.reply_text("You don't have permission to perform this action")
            return False
        return True

    @staticmethod
    def cancel(update, _):
        update.message.reply_text('Canceled')
        return ConversationHandler.END

    @staticmethod
    def fallback_register_callback(update, _):
        update.message.reply_text(
            'The name entered is invalid. Remember that it must be between 3 and 15 characters. It cannot contain spaces, symbols, or numbers.')

    @staticmethod
    def fallback_transaction_callback(update, _):
        update.message.reply_text('error')

    def reconnect(self, bot, update, n=True):
        try:
            if n is True:
                print("Reconectando")
        except ConnectionError:
            sleep(10)
            self.reconnect(False)

TELEGRAM = BotTelegram()
