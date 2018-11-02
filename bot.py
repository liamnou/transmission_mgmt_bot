#!/usr/bin/python3
# -*- coding: utf-8 -*-
import telebot
import configparser
import os
import transmissionrpc
import sys
import logging as log
import signal
import time


class Config():
    config = configparser.ConfigParser()
    config_file_path = None

    def __init__(self):
        self.config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
        self.load_config()

    def load_config(self):
        '''Load configuration parameters'''
        if os.path.exists(self.config_file_path):
            self.config.read(self.config_file_path)
        else:
            self.set_default_config()

    def set_default_config(self):
        '''Set default configuration'''
        self.config['telegram'] = {}
        self.config['telegram']['token'] = 'TELEGRAM_BOT_TOKEN'
        self.config['transmission'] = {}
        self.config['transmission']['transmission_host'] = 'localhost'
        self.config['transmission']['transmission_port'] = '9091'
        self.config['transmission']['transmission_user'] = 'admin'
        self.config['transmission']['transmission_password'] = ''
        self.config['transmission']['transmission_download_dir'] = ''

        with open(self.config_file_path, 'w') as config_file:
            self.config.write(config_file)

    def get(self):
        '''Obtain configuration'''
        return self.config


class Transmission:
    def __init__(self, config):
        self.config = config
        try:
            self.tc = transmissionrpc.Client(
                address=config['transmission']['transmission_host'],
                port=config['transmission']['transmission_port'],
                user=config['transmission']['transmission_user'],
                password=config.get['transmission']['transmission_password'],
                download_dir=config.get['transmission']['transmission_download_dir']
            )
        except transmissionrpc.error.TransmissionError:
            print("ERROR: Failed to connect to Transmission. Check rpc configuration.")
            sys.exit()

    def add_new_torrent(self, torrent_link):
        return self.tc.add_torrent(torrent_link)

    def get_torrents(self):
        return self.tc.get_torrents()


config = Config().get()
bot = telebot.TeleBot(config['telegram']['token'], threaded=False)

@bot.message_handler(commands=['start', 'help'])
def greet_new_user(message):
    welcome_msg = "\nWelcome to Transmission management bot!\nCommands available:\n" \
                  "/add - Add torrent to transfers list by URL or magnet link.\n" \
                  "/list - Print information for current torrents with provided ids\n" \
                  "/delete - Delete torrent from transfers list by ID\n" \
                  "/stop - Stop torrent by ID\n" \
                  "/start - Start torrent by ID\n" \
                  "/help - Print help message"
    if message.chat.first_name is not None:
        if message.chat.last_name is not None:
            bot.send_message(
                message.chat.id, "Hello, " + message.chat.first_name + " " + message.chat.last_name + welcome_msg
            )
        else:
            bot.send_message(message.chat.id, "Hello, " + message.chat.first_name + welcome_msg)
    else:
        bot.send_message(message.chat.id, "Hello, " + message.chat.title + welcome_msg)



@bot.message_handler(commands=['add'])
def add_new_torrent(message):
    torrent_link = message.text.replace('/add ', '', 1)
    transmission = Transmission(config)
    add_result = transmission.add_new_torrent(torrent_link)
    bot.send_message(
        message.chat.id, "Torrent was successfully added:\n{0}".format(add_result)
    )


@bot.message_handler(commands=['list'])
def list_all_torrents(message):
    transmission = Transmission(config)
    torrents = transmission.get_torrents()
    bot.send_message(
        message.chat.id, "{0}".format(torrents)
    )


def signal_handler(signal_number, frame):
    print('Received signal ' + str(signal_number)
          + '. Trying to end tasks and exit...')
    bot.stop_polling()
    sys.exit(0)


def main():
    log.basicConfig(level=log.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
    log.info('Bot was started.')

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            log.info('Starting bot polling...')
            bot.polling()
        except Exception as err:
            log.error("Bot polling error: {0}".format(err.args))
            bot.stop_polling()
            time.sleep(30)


if __name__ == '__main__':
    main()