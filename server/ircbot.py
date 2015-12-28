# -*- encoding: UTF-8 -*-
import re
import socket
import threading

class ircbot:
    sock = None
    chans = []

    def __init__(self, host, port, nick):
        print('[teebot_srv]', '[ircbot]', 'connect to {0}:{1}'.format(host, port))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.send(bytes('NICK ' + nick + '\n', 'utf-8'))
        self.sock.send(bytes('USER ' + nick + ' ' + nick + ' ' + nick + ' :' + nick + '\n', 'utf-8'))
    

    def join_chan(self, chan):
        print('[teebot_srv]', '[ircbot]', 'join', chan)
        self.sock.send(bytes('JOIN ' + chan + '\n', 'utf-8'))
        self.chans.append(chan)


    def ping(self):
        print('[teebot_srv]', '[ircbot]', 'ping!')
        self.sock.send(bytes('PONG :pingis\n', 'utf-8'))


    def send_msg(self, msg):
        print('[teebot_srv]', '[ircbot]', 'send msg:', msg)
        for chan in self.chans:
            self.sock.send(bytes('PRIVMSG ' + chan + ' :' + msg + '\n','utf-8'))


    def recv_msg(self, get_list):
        msg_pattern = re.compile(r':(.*?)!~.*?@.*? PRIVMSG (.*?) :(?u)(.*)')

        data = self.sock.makefile()
        for d in data:
            # print(d.strip('\n\r'))
            if (d.startswith('PING')):  # keep alive
                self.ping()
            msg_info = msg_pattern.match(d)
            if msg_info:
                man, chan, msg = msg_info.groups()
                print('[teebot_srv]', '[ircbot]', 'recv msg: {0}@{1}: {2}'.format(man, chan, msg))
                if msg.startswith('.tee'):
                    print('[teebot_srv]', '[ircbot]', 'recv command `.tee`')
                    reply = get_list()
                    self.send_msg(man + ': ' + reply)


    def start(self, get_list):
        t = threading.Thread(target = self.recv_msg, args = (get_list,))
        t.start()
