from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
from Tester import TESTER
from DataBase import DATABASE

TOKEN = '2128072171:AAES8w5dOuYV5e-0TbRq8h7Y6pV1KntEvDg'

class BotTelegram:
    def __init__(self):
        self.updater = Updater(TOKEN)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('state', self.state))
        self.dispatcher.add_handler(CommandHandler('stadistics', self.stadistics))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(CommandHandler('stadistics', self.stadistics))

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.broadcast))

        self.users = self.get_all_users()

    def run(self):
        self.updater.start_polling()
        #self.updater.idle()

    def stop(self):
        self.updater.stop()

    def echo(self, update: Update, context: CallbackContext) -> None:
        """Echo the user message."""
        print(update.message.chat.id)
        update.message.reply_text(update.message.text)

    def state(self, update: Update, context: CallbackContext) -> None:
        state = TESTER.test()['msg']
        update.message.reply_text(state)

    def start(self, update: Update, context: CallbackContext) -> None:
        new_id = update.message.chat.id
        registred = False
        self.help(update,context)
        for id in self.users:
            if id == new_id:
                registred = True
        if not registred:
            DATABASE.insert('telegram', 'code', new_id)
            self.users = self.get_all_users()

    def get_all_users(self):
        users = list()
        data = DATABASE.select('telegram')
        for user in data:
            users.append(user[1])
        return users


    def help(self, update: Update, context: CallbackContext) -> None:
        comands = 'Comands:\n /start\n /state\n /help'
        update.message.reply_text(comands)

    def notify(self, msg):
        for id in self.users:
            self.updater.bot.send_message(id, msg)

    def broadcast(self, update: Update, context: CallbackContext) -> None:
        id = update.message.chat.id
        if id == 1369437188:
            for user in self.users:
                if user != 1369437188:
                    self.updater.bot.send_message(user, update.message.text)

    def stadistics(self):
        pass


TELEGRAM = BotTelegram()
