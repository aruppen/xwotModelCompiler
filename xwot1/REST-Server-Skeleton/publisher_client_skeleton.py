import sys
import logging
import time
import json
import sqlite3

try:
    from twisted.web import resource
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

from templates.tpl_client import ClientElement

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

    def __updateClient(self, uri, method, accept):
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("Update Subscriber set uri='"+uri+"', method='"+method+"', accept='"+accept+"' where id='"+self.__pathname+"'")
        result = c.lastrowid
        conn.commit()
        c.close()
        conn.close()
        return result

    def __deleteQuery(self):
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        queryresult = c.execute("Delete from Subscriber where id='"+self.__pathname+"'")
        conn.commit()
        c.close()
        conn.close()
        return queryresult

    def __getClient(self):
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("Select * from Subscriber where id='"+self.__pathname+"'")
        result = c.fetchall()[0]
        c.close()
        conn.close()
        return result

    def render_OPTIONS(self, request):
        request.setResponseCode(http.NO_CONTENT)
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, PUT, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        logging.debug(request.requestHeaders)
        return ""

    def render_GET(self, request):
        """Handles GET requests"""
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        client = self.__getClient()
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, PUT, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                return str('{"id":"%s", "uri":"%s", "method":"%s", "accept":"%s"}' % (client[0], client[1], client[2], client[3]))
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                return str('<client><id>%s</id><uri>%s</uri><method>%s</method><accept>%s</accept></client>' % (client[0], client[1], client[2], client[3]))
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ClientElement(client[0], client[1], client[2], client[3])).addCallback(
                    request.write)
                request.finish()
                return NOT_DONE_YET

    def render_PUT(self, request):
        """Handles PUT request"""
        json_data = json.loads(request.content.getvalue())
        self.__updateClient(json_data["uri"], json_data["method"], json_data["accept"])
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        client = self.__getClient()
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, PUT, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                return str('{"id":"%s", "uri":"%s", "method":"%s", "accept":"%s"}' % (client[0], client[1], client[2], client[3]))
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                return str('<client><id>%s</id><uri>%s</uri><method>%s</method><accept>%s</accept></client>' % (client[0], client[1], client[2], client[3]))
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ClientElement(client[0], client[1], client[2], client[3], '')).addCallback(
                    request.write)
                request.finish()
                return NOT_DONE_YET

    def render_DELETE(self, request):
        """Handles DELETE request"""
        # TODO implement this
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        client = self.__getClient()
        self.__deleteQuery()
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        client = self.__getClient()
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, PUT, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                return str('{"id":"%s", "uri":"%s", "method":"%s", "accept":"%s"}' % (client[0], client[1], client[2], client[3]))
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                return str('<client><id>%s</id><uri>%s</uri><method>%s</method><accept>%s</accept></client>' % (client[0], client[1], client[2], client[3]))
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ClientElement(client[0], client[1], client[2], client[3], '')).addCallback(
                    request.write)
                request.finish()
                return NOT_DONE_YET


    def getChild(self, name, request):
        """delegate to child resource"""
        return $classname(self.datagen, name, self.__port, '')

