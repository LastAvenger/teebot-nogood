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
    'JOIN': player enter a server
    'LEAVE': player leave current server
'''

class server:
    sock = None
    clients = {}

    def __init__(self, port):
        print('[teebot_srv]', '[server]', 'listen on port:', port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.sock.bind((host, port))
        self.sock.listen(5)

    def recv(self, csock, addr, chan, send_msg):
        client_name = '[client-{0}]'.format(addr[0])

        try:
            data = csock.recv(128)
            tee_msg = json.loads(data.decode('utf-8'))

            if tee_msg['status'] != 'START':
                print('[teebot_srv]', '[server]', client_name, '**RECV WRONG STATUS**', 'connection close', tee_msg)
                csock.close()
                return

            self.clients[addr[0]] = tee_msg
        except:
            print('[teebot_srv]', '[server]', client_name, '**RECV WRONG DATA**')

        while True:
            try:
                data = csock.recv(128)

                if not data:
                    print('[teebot_srv]', '[server]', client_name, 'exit')
                    csock.close()
                    return

                tee_msg = json.loads(data.decode('utf-8'))
                print('[teebot_srv]', '[server]', client_name, 'recv:', tee_msg)

                if tee_msg['status'] != self.clients[addr[0]]:
                    self.clients[addr[0]] = tee_msg
                else:
                    print('[teebot_srv]', '[server]', client_name, '**RECV WRONG STATUS**')
            except:
                print('[teebot_srv]', '[server]', client_name, '**RECV WRONG DATA**')


    def start(self, chan, send_msg):
        while True:
            csock, addr = self.sock.accept()
            print('[teebot_srv]', '[server]', 'accept connection from', addr)
            t = threading.Thread(target = self.recv, args = (csock, addr, chan, send_msg))
            t.start()


    def get_list(self):
        reply = ''
        for _, v in self.clients.items():
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

    srv = server(port)

    task = threading.Thread(target = irc_bot.recv_msg, args = (srv.get_list,))
    task.start()

    srv.start(irc_chan, irc_bot.send_msg)

if __name__ == '__main__':
    main()
