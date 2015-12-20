#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import json
import socket
import threading
from ircbot import ircbot

'''
this dict is uesd to transmit between teebot client and server

{
    'player': '',   # player's name
    'status': '',   # player's status
    'server': '',   # server the player in
    'port': 0       # which port this server used
}

player's status:
    'START': player open teeworlds client
    'EXIT': player close teeworlds client   <- This one doesn't appear in server's playerlist
    'JOIN': player enter a server
    'LEAVE': player leave current server
'''

class playerlist:
    s = None
    plist = {}

    def __init__(self, port):
        print('[teebot_srv]', '[player_list]', 'listen on port:', port)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host = socket.gethostname()
        self.s.bind((host, port))

    def sync(self, chan, send_msg):
        data, addr = self.s.recvfrom(128)
        tee_msg = json.loads(data.decode('utf-8'))
        print('[teebot_srv]', '[player_list]', 'recv:', tee_msg)

        if not tee_msg['player'] in self.plist:
            if tee_msg['status'] != 'START':
                print('[teebot_srv]', '[player_list]', '**RECV WRONG STATUS**', tee_msg)
                print('recv status:', tee_msg)
                return
            else:
                print('[teebot_srv]', '[player_list]', tee_msg['player'], 'start tee!')
                send_msg(chan, tee_msg['player'] + ' start tee!')
        else:
            if tee_msg['status'] == 'EXIT':
                self.plist.pop(tee_msg['player'], None)
                print('[teebot_srv]', '[player_list]', tee_msg['player'], 'exit tee')
                send_msg(chan, tee_msg['player'] + ' exit tee')
                return
            elif tee_msg['status'] == 'START':
                print('[teebot_srv]', '[player_list]', '**RECV WRONG STATUS**')
                print('cur status:', self.plist[tee_msg['player']])
                print('recv status:', tee_msg)
                return

        self.plist[tee_msg['player']] = tee_msg


    def get_list(self):
        reply = ''
        for _, v in self.plist.items():
           if v['status'] == 'JOIN':
               reply = reply + '{0} {1}:{2}, '.format(v['player'], v['server'], v['port']) 
           elif v['status'] != 'EXIT':
               reply = reply + '{0}, '.format(v['player'])
        reply = reply[:-2]
        if not reply:
            reply = '{NULL}'
        return '=> ' + reply


def main():
    with open('./config.json') as f:
        conf = json.loads(f.read())
        port = conf['port']
        irc_host = conf['irc_host']
        irc_port = conf['irc_port']
        irc_chan = conf['irc_channel']
        irc_nick = conf['irc_nick']

    irc_bot = ircbot(irc_host, irc_port, irc_nick)
    irc_bot.join_chan(irc_chan)

    player_list = playerlist(port)

    task = threading.Thread(target = irc_bot.recv_msg, args = (player_list.get_list,))
    task.start()

    while True:
        player_list.sync(irc_chan, irc_bot.send_msg)

if __name__ == '__main__':
    main()
