# ##############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys
import signal
import logging
import getopt
import os
import time
import json
import socket

from pprint import pprint
from Arduino_Monitor import SerialData as DataGen
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

from WebSocketSupport import wotStreamerProtocol
from WebSocketSupport import HeartRateBroadcastFactory

$imports


class RestServer(object):
    def __init__(self, port='/dev/ttyACM0', path='/'):
        self.__port = port
        self.__path = path
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
        signal.signal(signal.SIGINT, self.signal_handler)

    def usage(self):
        print ('Usage:')
        print (os.path.basename(sys.argv[0]) + ' [option] ')
        print ('\033[1;33mWhere option is one of:\033[0m')
        print ('    -p path under which the service is deployed')
        print ('    -d Arduino dev for serial connection')
        print('     -s Serial delay for the serial connection')
        print ('    -h prints this help')

    def getArguments(self, argv):
        # Parse the command line options
        #if len(argv) == 0:
        #    self.usage()
        #    sys.exit(3)
        try:
            options, args = getopt.getopt(argv, "p:d:s:h", ["--help"])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)

        logging.debug("Parsing options")
        for option, arg in options:
            logging.debug("Passed options are  %s  and args are %s", option, arg)

            if option in ["-p"]:
                logging.info("Current WS path is: %s", arg)
                self.__path = "/" + arg
            elif option in ["-d"]:
                logging.info("Current Arudino dev is: %s", arg)
                self.__port = arg
            elif option in ["-s"]:
                logging.info("Current Delay is: %s", arg)
                self.__sdelay = arg
            elif option in ["-h"]:
                self.usage()
                sys.exit(2)
        logging.debug("Parsing arguments")
        for option, arg in options:
            logging.debug("Passed options are  \"%s\"  and args are \"%s\"", option, arg)
            if option in ["--help", "-h"]:
                self.usage()
                break
        self.run()

    def run(self):
        text_entry = ["User=ruppena", "Location=Fribourg", "Name=Udoo Temperature",
                      "Address=Bvd de Perolles 90, 1700 Fribourg"]
        service = ZeroconfService(name="Temperature (a) - " + socket.gethostname(), port=9000, text=text_entry)
        service.publish()
        data = DataGen(port=self.__port)
        logging.debug("Peparing Serial Connection. Please stand by...")
        time.sleep(self.__sdelay)
        ServerFactory = HeartRateBroadcastFactory
        factory = ServerFactory("ws://localhost:9000/", data, debug=False, debugCodePaths=False)
        factory.protocol = wotStreamerProtocol
        factory.setProtocolOptions(allowHixie76=True)

        ws_resource = WebSocketResource(factory)
        root = File('.')
        root.indexNames = ['rest-documentation.html']
        root.putChild('temperature', ws_resource)
        $pathdef
        site = Site(root)
        #site.protocol = HTTPChannelHixie76Aware # needed if Hixie76 is to be supported
        reactor.listenTCP(9000, site)
        reactor.run()


    def signal_handler(self, signal, frame):
        logging.info('Stopping now')
        sys.exit(0)

if __name__ == '__main__':
    hrm = RestServer();
    hrm.getArguments(sys.argv[1:])
    #service = ZeroconfService(name="TestService", port=3000)
    #service.publish()
    #raw_input("Press any key to unpublish the service ")
    #service.unpublish()

   

