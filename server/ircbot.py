# -*- encoding: UTF-8 -*-
import re
import socket

class ircbot:
    sock = None
    chans = []

    def __init__(self, host, port, nick):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.send(bytes('NICK ' + nick + '\n', 'utf-8'))
        self.sock.send(bytes('USER ' + nick + ' ' + nick + ' ' + nick + ' :' + nick + '\n', 'utf-8'))
    

    def join_chan(self, chan):
        self.sock.send(bytes('JOIN ' + chan + '\n', 'utf-8'))
        self.chans.append(chan)


    def ping(self):
        self.sock.send(bytes('PONG :pingis\n', 'utf-8'))


    def send_msg(self, chan, msg):
        self.sock.send(bytes('PRIVMSG ' + chan + ' :' + msg + '\n','utf-8'))


    def recv(self):
        msg_pattern = re.compile(r':(.*?)!~.*?@.*? PRIVMSG (.*?) :(?u)(.*)')

        data = self.sock.makefile()
        for d in data:
            print(d.strip('\n\r'))
            if (d.startswith('PING')):  # keep alive
                self.ping()
            msg_info = msg_pattern.match(d)
            if msg_info:
                man, chan, msg = msg_info.groups()
                if msg.startswith('.tee'):
                    self.send_msg(chan,  man + ': tee!')


