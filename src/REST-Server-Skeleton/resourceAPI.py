import sys
import signal
import logging
import getopt
import os
import time


import json


import socket

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
    
from WebSocketSupport import wotStreamerProtocol
from WebSocketSupport import HeartRateBroadcastFactory

$import

class $classname(resource.Resource):
    """
   Simple Handler for the temperature resource. Only responds to GET request in either json or xml format.
    """
   
    def __init__(self,  datagen,  messageStore):
        resource.Resource.__init__(self)
        self.datagen = datagen
    
    def render_GET(self,  request):
        self.data = self.datagen.next()
        #pprint(request.__dict__)
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        if not None:
            if accept_type == "application/json":
                request.setResponseCode(202)
                request.setHeader("Content-Type",  "application/json; charset=UTF-8")
                return str('{"xwot": %s, "timestamp": "%d"}'% (self.data,   time.time()))
            else: #elif accept_type == "application/xml":
                request.setResponseCode(202)
                request.setHeader("Content-Type",  "application/xml; charset=UTF-8")
                return str('<?xml version="1.0"?><xwot>%s</xwot><timestamp>%d</timestamp></measure>'% (self.data,   time.time()))
                
    def getChild(self, name, request):
        """some comments"""
        $child

