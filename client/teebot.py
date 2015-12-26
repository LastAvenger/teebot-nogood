#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import os
import re
import json
import socket
import subprocess

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

class client:
    sock = None
    stat = {
            "player": '',
            "status": '',
            "server": '',
            "port": 0
            }

    def dict2byte(self, d):
        return bytes(str(json.dumps(d)), 'utf-8')


    def __init__(self, host, port, player):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        print('[teebot]', '[client]', 'connect to ', (host, port))
        self.sock.connect((host, port))

        self.stat['player'] = player
        self.send('START')


    def send(self, status, server = '', port = 0):
        if status == 'EXIT':
            self.sock.close()
            return
        if status == self.stat['status'] == 'JOIN':
            return
        if status == 'LEAVE' and self.stat['status'] != 'JOIN':
            return

        self.stat['status'] = status
        self.stat['server'] = server
        self.stat['port'] = port

        print('[teebot]', '[client]', 'send:', self.stat)
        self.sock.send(self.dict2byte(self.stat))


def main():
    with open('./config.json') as f:
        conf = json.loads(f.read())
        port = conf['port']
        server = conf['server']
        game = conf['game']

    tee_conf = os.path.expanduser('~') + '/.teeworlds/'
    if game == 'teeworlds':
        tee_conf = tee_conf + 'settings.cfg'
    elif game == 'ddnet':
        tee_conf = tee_conf + 'settings_ddnet.cfg'
    else:
        print('[teebot]',  'wrong game value')
        exit(-1)

    with open(tee_conf) as f:
        for l in f.readlines():
            if l.startswith('player_name'):
                player = l.split('"', 2)[1]
                break
        else:
            print('[teebot]', '[config]' ,'can not find player_name in', tee_conf)
            exit(-1)

    print('[teebot]', player, 'start tee!')
    c = client(server, port, player)

    leave_pattern = re.compile(r"\[[0-9a-f\-: ]+\]\[client\]: disconnecting. reason='(.*)'")
    join_pattern = re.compile(r"\[[0-9a-f\-: ]+\]\[client\]: connecting to '([0-9.]+?):([0-9]+)'")
    with subprocess.Popen([game], stdout = subprocess.PIPE) as p:
        while True:
            line = p.stdout.readline()
            if not line:    # leave game
                break
            line = line.decode('utf-8')

            leave_info = leave_pattern.match(line)
            join_info = join_pattern.match(line)

            if leave_info:
                c.send('LEAVE')

            if join_info:
                game_srv, game_port = join_info.groups()
                c.send('JOIN', server= game_srv, port = int(game_port))

    c.send('EXIT')
    print('[teebot]', player, 'leave tee')

if __name__ == '__main__':
    main()

