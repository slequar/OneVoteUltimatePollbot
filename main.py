# Token = 850280100:AAECV30SkFq8wsUMrQd2NPnbjMdabr9ZuMk

import telegram
import sys, os

from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class OVPoll():
    '''The One-Vote Poll class'''
    def __init__(self):
        self.options = []
        self.question = ''
        self.answer = None
        self.done = False

    def is_valid(self):
        return (self.question != '') and (len(self.options) > 0)

    def is_done(self):
        return self.done

    def is_over(self):
        return self.answer != None

    def set_question(self, question):
        self.question = question

    def add_option(self, option):
        self.options += [option]

    def finish(self):
        self.done = True

    def generate_text_poll(self):
        text_poll = "One Vote Ultimate Poll:\n" + self.question
        for option in self.options:
            text_poll += ('\n- ' + option)
        return text_poll

    def generate_markdown_poll(self):
        buttons = [[InlineKeyboardButton(option, callback_data=i+1)] for i, option
                    in enumerate(self.options)]
        print('button1')
        buttons = [[InlineKeyboardButton("Share Poll", switch_inline_query="")] for i, option
                    in enumerate(self.options)]
        print('button2')
        return InlineKeyboardMarkup(buttons)

    def markdown_options(self):
        return InlineKeyboardMarkup([[InlineKeyboardButton(text="Send Poll", switch_inline_query=")]])




def start(update, context):
    print("start1")
    # keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
    #              InlineKeyboardButton("Option 2", callback_data='2')],
    #
    #             [InlineKeyboardButton("Option 3", callback_data='3')]]
    # keyboard = [[InlineKeyboardButton(i, callback_data=i)] for i in range(1,4)]
    #
    # reply_markup = InlineKeyboardMarkup(keyboard)
    #
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)
    with open("data/start.txt", "r") as text:
        pass



def new_poll(update, context):
    print("newpoll1")
    context.user_data['ovpoll'] = OVPoll()
    update.message.reply_text('Send me the question for your poll')

def message(update, context):
    print("we got messaggg")
    try:
        poll = context.user_data['ovpoll']
        print(type(poll))
    except KeyError as e:
        print("keyerror")
        return

    # print("messag2")
    # print(poll.question, poll.is_valid(), poll.is_done(), poll.is_over())
    if not(poll.is_done()):
        if poll.question == '':
            print("need q")
            poll.set_question(update.message.text)
            update.message.reply_text('Send me an option for the poll')
        else:
            print("add opt")
            poll.add_option(update.message.text)
            update.message.reply_text('Send me another option for the poll or /done to end')

def vote(update, context):
    print("voting")
    poll = update.callback_query['message']['text'].split('\n')
    index = int(update.callback_query['data'])+1

    final_poll = '\n'.join(poll[:2]) + '\n>>> ' + poll[index][2:]
    for i in poll[2:]:
        if i != poll[index]:
            final_poll += '\n' + i
    update.callback_query.edit_message_text(final_poll)


def done(update, context):
    print("done1")
    try:
        poll = context.user_data['ovpoll']
    except KeyError as e:
        return

    print("done2")
    if poll.is_valid():
        print("finish Him")
        poll.finish()
        temp = update.message.reply_text(poll.generate_text_poll(), reply_markup=poll.generate_markdown_poll())
        #update.message.reply_markdown(poll.generate_markdown_poll())
        #temp.edit_reply_markup(poll.generate_markdown_poll())
        print("done3")



def main():
    TOKEN = "850280100:AAECV30SkFq8wsUMrQd2NPnbjMdabr9ZuMk"
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newpoll', new_poll))
    updater.dispatcher.add_handler(CommandHandler('done', done))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, message))
    updater.dispatcher.add_handler(CallbackQueryHandler(vote))


    updater.start_polling()
    print("bot started")
    updater.idle()


if __name__ == "__main__":
    main()
