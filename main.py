# Token = 850280100:AAECV30SkFq8wsUMrQd2NPnbjMdabr9ZuMk

import telegram
import sys, os, logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup,\
                     InlineQueryResultDocument, InputTextMessageContent
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler,\
                         InlineQueryHandler, Updater, Filters


# -----------
# The class for the One-Vote Polls
# -----------

class OVPoll():
    '''The One-Vote Poll class'''
    def __init__(self, owner, index):
        self.options = []
        self.owner = owner
        self.question = ''
        self.answer = None
        self.done = False
        self.index = index

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

    def vote(self, option):
        self.answer = self.options[option-1]

    def generate_text_poll(self):
        '''Text version of the poll shown to users'''
        text_poll = "One Vote Ultimate Poll:\n" + self.question
        for option in self.options:
            text_poll += ('\n- ' + option)
        return text_poll

    def generate_markdown_poll(self):
        '''Interactive buttons displayed under text poll'''
        buttons = [[InlineKeyboardButton(option, callback_data=str([self.owner, self.index, i+1]))] for i, option
                    in enumerate(self.options)]
        return InlineKeyboardMarkup(buttons)

    def sending_options(self):
        '''Send Poll button for creator of poll'''
        return InlineKeyboardMarkup([[InlineKeyboardButton(text="Send Poll", switch_inline_query=str(self.index))]])


# -----------
# The telegram slashtag commands
# -----------

def start(update, context):
    with open("data/start.txt", "r") as text:
        update.message.reply_text(text.readline())


def new_poll(update, context):
    '''Starts poll creation process'''
    user = update.effective_user.id
    if user not in user_polls.keys():
        user_polls[user] = {'current': 0}
    polls = user_polls[user]
    curr = polls['current']

    if curr not in polls.keys() or not(polls[curr].is_done()):
        polls[curr] = OVPoll(user, curr)
    else:
        polls[curr + 1] = OVPoll(user, curr + 1)
        polls['current'] += 1

    temp = update.message.reply_text('Send me the question for your poll')


def done(update, context):
    '''This command finishes the creation of a poll if it is valid'''
    user = update.effective_user.id
    try:
        polls = user_polls[user]
        poll = polls[polls['current']]
    except KeyError as e:
        return

    if poll.is_valid() and not(poll.is_done()):
        poll.finish()
        update.message.reply_text(poll.generate_text_poll(), reply_markup=poll.sending_options())


def cancel(update, context):
    '''This command cancels creation of an active poll'''
    user = update.effective_user.id
    try:
        polls = user_polls[user]
        if not(polls[polls['current']].is_done()):
            polls.pop(polls['current'])
            if polls['current']!= 0:
                polls['current'] -= 1
            update.message.reply_text("poll canceled")
    except KeyError:
        # any keyerror is a case where /cancel isn't a valid command
        pass


# -----------
# Handling the rest of the Telegram events
# -----------

def message(update, context):
    '''Responds only to messages in the creation process'''
    user = update.effective_user.id
    try:
        polls = user_polls[user]
        poll = polls[polls['current']]
    except KeyError as e:
        return

    if not(poll.is_done()):
        if poll.question == '':
            poll.set_question(update.message.text)
            update.message.reply_text('Send me an option for the poll')
        else:
            poll.add_option(update.message.text)
            update.message.reply_text('Send me another option for the poll, /done to end, or /cancel to cancel')


def vote(update, context):
    '''
    This function runs when a vote is cast by hitting the appropriate button in
    an active poll
    '''
    a = eval(update.callback_query['data'])
    try:
        poll = user_polls[a[0]][a[1]]
        text_poll = poll.generate_text_poll().split('\n')
        index = a[2] + 1
    except KeyError as e:
        # FIXME this error throws when the bot has been restarted and loses
        # the poll data. Could be fixed with a database.
        return

    if(text_poll[0] == "One Vote Ultimate Poll:"):
        final_poll = '\n'.join(text_poll[:2]) + '\n>>> ' + text_poll[index][2:]
        for i in text_poll[2:]:
            if i != text_poll[index]:
                final_poll += '\n' + i
        poll.vote(a[2])
        update.callback_query.edit_message_text(final_poll)


def send_inline(update, context):
    '''This function handles sending polls through inline queries'''
    user = update.effective_user.id
    try:
        polls = user_polls[user]
    except KeyError as e:
        return

    # FIXME eventually this should display all polls if no query is given
    if update.inline_query['query'] != 'all':
        try:
            poll = polls[int(update.inline_query['query'])]
            context.bot.answer_inline_query(update.inline_query.id,
                [InlineQueryResultDocument(1, "https://t.me/" + str(update.inline_query.id), poll.question, 'application/pdf',
                input_message_content=InputTextMessageContent(poll.generate_text_poll()),
                reply_markup=poll.generate_markdown_poll())], cache_time=0)
        except KeyError:
            pass
        except ValueError:
            pass
    else:
        poll_list = list(polls.values())
        poll_list.remove(polls['current'])
        if len(poll_list) > 0:
            context.bot.answer_inline_query(update.inline_query.id,
                [InlineQueryResultDocument(1, "https://t.me/" + str(update.inline_query.id), poll.question, 'application/pdf',
                input_message_content=InputTextMessageContent(poll.generate_text_poll()),
                reply_markup=poll.generate_markdown_poll()) for poll in poll_list], cache_time=0)


# -----------
# Running the bot
# -----------

def main():
    TOKEN = "850280100:AAECV30SkFq8wsUMrQd2NPnbjMdabr9ZuMk"
    updater = Updater(TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('newpoll', new_poll))
    updater.dispatcher.add_handler(CommandHandler('done', done))
    updater.dispatcher.add_handler(CommandHandler('cancel', cancel))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, message))
    updater.dispatcher.add_handler(CallbackQueryHandler(vote))
    updater.dispatcher.add_handler(InlineQueryHandler(send_inline))

    logging.basicConfig(
        filename="data/bot.log",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater.start_polling()
    updater.idle()

# user_polls is a dictionary of dictionaries, with user_id:polls, and inside
# the polls dictionary, polls are referenced by (int):(OVPoll). polls also
# includes the 'current':(int), which is the index of the most recent poll
user_polls = {}

if __name__ == "__main__":
    main()
