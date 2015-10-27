import sys
import logging
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

    def render_GET(self, request):
        """Handles GET requests"""
        # TODO implement this
        json_data = json.loads('{"temperature":"-100","humidity":"-100"}')
        # pprint(request.__dict__)
        json_data = json.loads('{"temperature":"-100","humidity":"-100"}')
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                # TODO implement JSON response
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                # TODO implement XML response
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ExampleElement(json_data['temperature'], json_data['humidity'])).addCallback(
                    request.write)
                request.finish()
                # TODO implement HTML response
                return NOT_DONE_YET

    def render_POST(self, request):
        """Handles POST request"""
        # TODO implement this
        json_data = json.loads('{"temperature":"-100","humidity":"-100"}')
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                # TODO implement JSON response
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                # TODO implement XML response
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ExampleElement(json_data['temperature'], json_data['humidity'])).addCallback(
                    request.write)
                request.finish()
                # TODO implement HTML response

    def render_PUT(self, request):
        """Handles PUT request"""
        # TODO implement this
        json_data = json.loads('{"temperature":"-100","humidity":"-100"}')
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                # TODO implement JSON response
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                # TODO implement XML response
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ExampleElement(json_data['temperature'], json_data['humidity'])).addCallback(
                    request.write)
                request.finish()
                # TODO implement HTML response
$render_method



    def getChild(self, name, request):
        """some comments"""
        $child

