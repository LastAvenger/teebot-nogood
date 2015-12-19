#!/usr/bin/env python3
# -*- encoding: UTF-8 -*-
import os
import re
import json
import socket
import subprocess

'''
`tee_msg` uesd to transmit between teebot client and server

tee_msg = {
        'player': '',   # player's name
        'status': '',   # player's status
        'server': '',   # server the player in
        'port': 0       # which port this server used
        }

player's status:
    'START': player open teeworlds client and prepares for game
    'EXIT': player close teeworlds client
    'JOIN': player enter a server
    'LEAVE': player leave current server
'''


sock = None

def dict2byte(d):
    return bytes(str(json.dumps(d)), 'utf-8')


def connect_to_srv(host, port):
    print('[teebot]', '[net]', 'connect to', host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    return sock


def updata_stat(sock, msg):
    print('[teebot]', '[net]', msg)
    sock.send(dict2byte(msg))


def main():
    tee_msg = {
            "player": '',
            "status": '',
            "server": '',
            "port": 0
            }

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
        print('[teebot]',  'wrong *game* value')
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
    tee_msg['player'] = player
    tee_msg['status'] = 'START'
    s = connect_to_srv(server, port)
    updata_stat(s, tee_msg)

    leave_pattern = re.compile(r"\[[0-9a-f]+\]\[client\]: disconnecting. reason='(.*)'")
    enter_pattern = re.compile(r"\[[0-9a-f]+\]\[client\]: connecting to '([0-9.]+?):([0-9]+)'")
    with subprocess.Popen([game], stdout = subprocess.PIPE) as p:
        while True:
            line = p.stdout.readline()
            if not line:    # leave game
                break
            sline = line.decode('utf-8')

            leave_info = leave_pattern.match(sline)
            if leave_info and tee_msg['status'] == 'JOIN':
                reason = leave_info.group(1)
                print('[teebot]', '[status]', player, 'leave server, reason:', reason)
                tee_msg['status']  = 'LEAVE'
                updata_stat(s, tee_msg)

            join_info = enter_pattern.match(sline)
            if join_info and tee_msg['status'] != 'JOIN':
                game_srv = join_info.group(1)
                gmae_port = int(join_info.group(2))
                print('[teebot]', '[status]', player, 'join server:', game_srv + ':', gmae_port)
                tee_msg['status']  = 'JOIN'
                tee_msg['server']  = game_srv
                tee_msg['port']  = gmae_port
                updata_stat(s, tee_msg)

    print('[teebot]', player, 'leave game')

if __name__ == '__main__':
    main()

