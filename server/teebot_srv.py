#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import json
import socket
from ircbot import ircbot

def main():
    with open('./config.json') as f:
        conf = json.loads(f.read())
        port = int(conf['port'])
        irc_host = conf['irc']['host']
        irc_port = int(conf['irc']['port'])
        irc_chan = conf['irc']['channel']
        irc_nick = conf['irc']['nick']

    irc_bot = ircbot(irc_host, irc_port, irc_nick)
    irc_bot.join_chan(irc_chan)
    irc_bot.send_msg(irc_chan, 'hi')
    while True:
        irc_bot.recv()

if __name__ == '__main__':
    main()
