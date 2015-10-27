#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #############################################################################################################
# REST server component which is deployed on smart devices. This is the main class and entry point #
# ---------------------------------------------------------------------------------------------------------- #
#                                                                                                            #
# Author: Andreas Ruppen                                                                                     #
# License: GPL                                                                                               #
# This program is free software; you can redistribute it and/or modify                                       #
#   it under the terms of the GNU General Public License as published by                                     #
#   the Free Software Foundation; either version 2 of the License, or                                        #
#   (at your option) any later version.                                                                      #
#                                                                                                            #
#   This program is distributed in the hope that it will be useful,                                          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                            #
#   GNU General Public License for more details.                                                             #
#                                                                                                            #
#   You should have received a copy of the GNU General Public License                                        #
#   along with this program; if not, write to the                                                            #
#   Free Software Foundation, Inc.,                                                                          #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                                                #
##############################################################################################################

import sys
import signal
import logging
import time
import socket
import argparse

# either import this for Arduino on Serial Bus
from Hardware_Monitor import SerialData as DataGen
# or imort this for Raspberry Pis
#from Hardware_Monitor import RPData as DataGen

from ZeroconfigService import ZeroconfService

try:
    from twisted.web import resource
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.web.server import Site
    from twisted.web.static import File
    from autobahn.twisted.resource import WebSocketResource, HTTPChannelHixie76Aware
    from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
except:
    print 'Some dependendencies are not met'
    print 'You need the following packages: twisted, autobahn'
    print 'install them via pip'
    sys.exit()

$imports


class RestServer(object):
    def __init__(self, device='/dev/ttyACM0', port=9000):
        self.__device = device
        self.__port = port
        self.__sdelay = 1
        """Do some initialization stuff"""
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(levelname) -7s] %(asctime)s  %(module) -20s:%(lineno)4s %(funcName)-20s %(message)s',
                            filename='sms.log',
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the sys.stderr other are CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)
        #signal.signal(signal.SIGINT, self.signal_handler)

    def getArguments(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--port", help="port under which the service is deployed (default 9000)", type=int, default=9000,
                            required=False)
        parser.add_argument('-d', '--dev', help='Arduino dev for serial connection (default /dev/ttyACM0)', type=str, default='/dev/ttyACM0',
                            required=False)
        parser.add_argument('-s', '--delay', help='Serial delay for the serial connection (default 10)', type=int, default=10,
                            required=False)
        args = parser.parse_args(argv)
        self.__port = args.port
        self.__device = args.dev
        self.__sdelay = args.delay

        self.run()

    def run(self):
        text_entry = {"User": "ruppena", "Location": "Fribourg", "Name": "Udoo Temperature",
                      "Address": "Bvd de Perolles 90, 1700 Fribourg"}
        service = ZeroconfService(name="Temperature (a) - " + socket.gethostname(), port=self.__port, text=text_entry)
        service.publish()
        data = DataGen(port=self.__device)

        logging.info("Peparing Serial Connection. Please stand by...")
        time.sleep(self.__sdelay)
        logging.info("Up and Running")

        root = File('.')
        root.indexNames = ['rest-documentation.html']
        $pathdef
        site = Site(root)
        #site.protocol = HTTPChannelHixie76Aware # needed if Hixie76 is to be supported
        reactor.listenTCP(self.__port, site)
        reactor.run()


    #def signal_handler(self, signal, frame):
    #    logging.info('Stopping now')
    #    sys.exit(0)

if __name__ == '__main__':
    hrm = RestServer()
    hrm.getArguments(sys.argv[1:])

   

