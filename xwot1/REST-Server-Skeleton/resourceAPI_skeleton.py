import sys
import logging
import time
import json

try:
    from twisted.web import resource, http
    from twisted.web.template import Element, renderer, XMLFile, flattenString
    from twisted.web.server import Site, NOT_DONE_YET
    from twisted.web.static import File
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.python.filepath import FilePath
    from autobahn.twisted.resource import WebSocketResource, HTTPChannelHixie76Aware
    from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS
except:
    print 'Some dependendencies are not met'
    print 'You need the following packages: twisted, autobahn, websocket'
    print 'install them via pip'
    sys.exit()

from templates.tpl_temperature import ExampleElement

$import


class $classname(resource.Resource):
    """
   Simple Handler for the temperature resource. Only responds to GET request in either json or xml format.
    """
    isLeaf = False

    def __init__(self, datagen, pathname, port, messageStore):
        resource.Resource.__init__(self)
        self.__pathname = pathname
        self.__port = port
        self.datagen = datagen

    def render_OPTIONS(self, request):
        request.setResponseCode(http.NO_CONTENT)
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        logging.debug(request.requestHeaders)
        return ""

$render_method


    def getChild(self, name, request):
        """some comments"""
        $child

