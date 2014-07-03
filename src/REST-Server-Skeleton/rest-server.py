###############################################################################
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
    from twisted.web import  resource
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.web.server import Site
    from twisted.web.static import File
    from autobahn.twisted.resource import WebSocketResource,  HTTPChannelHixie76Aware
    from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
except:
    print 'Some dependendencies are not met'
    print 'You need the following packages: twisted, autobahn, websocket'
    print 'install them via pip'
    sys.exit()
    
$imports    


class wotStreamerProtocol(WebSocketServerProtocol):
   """
   Very basic WebSocket Protocol. All clients are accepted. Furthermore received messages are fowarded to all clients.
   """
    
   def onOpen(self):
      self.factory.register(self)

   def onMessage(self, payload, isBinary):
      if not isBinary:
         msg = "{} from {}".format(payload.decode('utf8'), self.peer)
         self.factory.broadcast(msg)

   def connectionLost(self, reason):
      WebSocketServerProtocol.connectionLost(self, reason)
      self.factory.unregister(self)


class HeartRateBroadcastFactory(WebSocketServerFactory):
   """
   Broadcasts the Temperature at regular intervalls to all connected clients.
   """

   def __init__(self,  url,  datagen,  debug=False,  debugCodePaths=False):
        WebSocketServerFactory.__init__(self,  url,  debug = debug,  debugCodePaths = debugCodePaths)
        self.clients = []
        self.tickcount = 0
        self.datagen = datagen
        self.data = [self.datagen.next_two()]
        self.lastbroadcast = 0
        self.tick()
        self.acquiredata()
        
   def acquiredata(self):
        #measure = round(self.datagen.next_two()[0],  2)
        localdata = self.datagen.next_two()
        #pprint(localdata)
        if isinstance(localdata,  list) and len(localdata)>=2:
            temp = round(localdata[0],  2)
            humidity = round(localdata[1],  2)
        else:
                temp = -100
                humidity = -100
        millis = int(round(time.time() * 1000))
        if((temp != self.data[len(self.data)-1][0]) or (humidity != self.data[len(self.data)-1][1]) or (millis - self.lastbroadcast)>10000):
            self.lastbroadcast = millis
            self.data.append(localdata)
            try:
                #self.broadcast('{ "temperature" : %5.2f, "units" : "celsius", "precision" : "2" }' % self.data[len(self.data)-1])
                #self.broadcast('{"measure": {"temperature": "%5.2f","units": "celsius","precision": "2", "timestamp": "%d"}}' % (self.data[len(self.data)-1],  time.time()))
                self.broadcast('{"temperature": {"@units": "celsisus","@precision": "2","#text": "%5.2f"},"humidity": {"@units": "celsisus","@precision": "2","#text": "%5.2f"}, "timestamp": "%d"}' % (self.data[len(self.data)-1][0], self.data[len(self.data)-1][1],  time.time()))
            except TypeError:
                logging.error("no value") 
        reactor.callLater(1,  self.acquiredata)

   def tick(self):
      self.tickcount += 1
      self.broadcast("tick %d from server" % self.tickcount)
      reactor.callLater(299, self.tick)

   def register(self, client):
      if not client in self.clients:
         logging.debug('registered client ' + client.peer)
         self.clients.append(client)

   def unregister(self, client):
      if client in self.clients:
         logging.debug("unregistered client " + client.peer)
         self.clients.remove(client)

   def broadcast(self, msg):
      logging.debug("broadcasting prepared message '{}'".format(msg))
      preparedMsg = self.prepareMessage(msg)
      for c in self.clients:
         c.sendPreparedMessage(preparedMsg)
         logging.debug("prepared message sent to {}".format(c.peer))


class HeartRateMonitor(object):
    def __init__(self, port='/dev/ttyACM0', path='/'):
        self.__port = port
        self.__path = path
        """Do some initialization stuff"""
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
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
        print (os.path.basename(sys.argv[0])+' [option] ') 
        print ('\033[1;33mWhere option is one of:\033[0m')
        print ('    -p path under which the service is deployed')
        print ('    -d Arduino dev for serial connection')
        print ('    -h prints this help')

    def getArguments(self, argv):
        # Parse the command line options
        #if len(argv) == 0:
        #    self.usage()
        #    sys.exit(3)
        try:
            options, args = getopt.getopt(argv, "p:d:h", ["--help"])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)

        logging.debug("Parsing options")
        for option, arg in options:
            logging.debug("Passed options are  %s  and args are %s", option, arg)

            if option in ["-p"]:
                logging.info("Current WS path is: %s", arg)
                self.__path="/"+arg
            elif option in ["-d"]:
                logging.info("Current Arudino dev is: %s", arg)
                self.__port=arg
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
        text_entry = ["User=ruppena", "Location=Fribourg", "Name=Udoo Temperature", "Address=Bvd de Perolles 90, 1700 Fribourg"]
        service = ZeroconfService(name="Temperature (a) - "+socket.gethostname(),  port=9000,  text=text_entry)
        service.publish()
        data = DataGen(port=self.__port)
        logging.debug("Peparing Serial Connection. Please stand by...")
        time.sleep(10)
        ServerFactory = HeartRateBroadcastFactory
        factory = ServerFactory("ws://localhost:9000/",  data, debug = False,  debugCodePaths = False)
        factory.protocol = wotStreamerProtocol
        factory.setProtocolOptions(allowHixie76 = True)
        
        #listenWS(factory)
        #webdir = File(".")
        #web = Site(webdir)
        #reactor.listenTCP(8080, web)
        #reactor.run()
        
        
        ws_resource = WebSocketResource(factory)
        root = File('.')
        root.indexNames=['rest-documentation.html']
        root.putChild('temperature',  ws_resource)
        $pathdef
        site = Site(root)
        #site.protocol = HTTPChannelHixie76Aware # needed if Hixie76 is to be supported
        reactor.listenTCP(9000,  site)
        reactor.run()
        
        
    def signal_handler(self,  signal,  frame):
        logging.info('Stopping now')
        sys.exit(0)

    
if __name__ == '__main__':
    hrm = HeartRateMonitor();
    hrm.getArguments(sys.argv[1:])
    #service = ZeroconfService(name="TestService", port=3000)
    #service.publish()
    #raw_input("Press any key to unpublish the service ")
    #service.unpublish()

   
