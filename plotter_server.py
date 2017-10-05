#! /usr/bin/env python2.7
"""plotter_server

Usage:
  plotter_server.py [port]
"""

from __future__ import print_function
import sys
import os
from socket import socket, AF_INET, SOCK_DGRAM
from chiplotle.tools.plottertools import instantiate_plotters
from serial.serialutil import SerialException

class PlotterNotConnectedException(Exception):
    pass

class Plotter(object):
    def __init__(self):
        try:
            plotters = instantiate_plotters()
            if len(plotters) > 0:
                self.device = plotters[0]
            else:
                raise PlotterNotConnectedException()
        except SerialException:
            raise PlotterNotConnectedException()

    
    def plot(self, filepath):
        try:
            with open(filepath) as f:
                hpgl = f.read()
                hpgl = ''.join(hpgl.split())
            self.device.write(hpgl)
            # call flush() to wait till all data is written before exiting...
            self.device._serial_port.flush()
            return True
        except IOError:
            return False

if __name__ == '__main__':

    if len(sys.argv) < 2:
        port = 6574
    else:
        port = int(sys.argv[1])

    try:
        plotter = Plotter()
    except PlotterNotConnectedException:
        print('No plotter connected')
    else:
        sock = socket(AF_INET, SOCK_DGRAM)
        addr = ('0.0.0.0', port)
        sock.bind(addr)
        print('Listening on port', port)

        try:
            while True:
                filepath, address = sock.recvfrom(4096)
                print('Attempting to plot {}...'.format(os.path.basename(filepath)))
                if plotter.plot(filepath):
                    print('Done')
                else:
                    print("Can't plot file")
        except KeyboardInterrupt:
            pass
        
        
    
