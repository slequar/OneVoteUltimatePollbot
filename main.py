#aaaaa
# Token = 850280100:AAECV30SkFq8wsUMrQd2NPnbjMdabr9ZuMk

import telegram
import sys, os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters



class OVPoll():

    def __init__(self):
        self.options = []
        self.question = ''
        self.answer = ''

    def is_created(self):
        return self.question != '' and self.options.len > 0

    def is_done(self):
        return self.answer != ''








def start(update, context):
    temp = update.message.reply_text('works')
    print(type(temp))
    print(temp.text)
    temp.edit_text('works22')
    with open("data/start.txt", "r") as text:
        pass

def new_poll(update, context, user_data):
    user_data['ovpoll']
    update.message.reply_text('Send me the question for your poll')

def message(update, context, user_data):
    pass



def main():
    TOKEN = "850280100:AAECV30SkFq8wsUMrQd2NPnbjMdabr9ZuMk"
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
    updater.dispatcher.add_handler(CommandHandler('newpoll', new_poll, pass_user_data=True))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, message, pass_user_data=True))





    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
