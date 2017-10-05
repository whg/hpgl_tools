#! /usr/bin/env python3
"""hpgl_sender

Usage:
  hpgl_sender.py <file> [-a IP] [-p PORT]
  hpgl_sender.py (-h | --help)
  hpgl_sender.py --version

Options:
  -h --help        Show this screen
  --version        Show version
  -p PORT          Port number to listen on [default: 6574]
  -a IP            IP of server [default: localhost]
"""

from os import path
from socket import socket, AF_INET, SOCK_DGRAM
from docopt import docopt

if __name__ == "__main__":
    args = docopt(__doc__, version=0.1)

    filepath = args['<file>']
    if filepath[0] != '/':
        current_dir = path.dirname(path.realpath(__file__))
        filepath = path.join(current_dir, args['<file>'])

    sock = socket(AF_INET, SOCK_DGRAM)
    addr = (args['-a'], int(args['-p']))

    sock.sendto(filepath.encode('utf8'), addr)
