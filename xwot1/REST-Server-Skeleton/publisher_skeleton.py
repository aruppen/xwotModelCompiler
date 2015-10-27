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

from templates.tpl_clients import ClientsElement
from templates.tpl_client import ClientElement
from WebSocketSupport import wotStreamerProtocol
from WebSocketSupport import HeartRateBroadcastFactory

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

    def __getAllClients(self):
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("Select * from Subscriber where resourceid=1 order by id")
        result = c.fetchall()
        c.close()
        conn.close()
        return result

    def __insertClient(self, uri, method, accept, event=''):
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("insert into Subscriber (uri, method, accept, resourceid) values ('"+uri+"', '"+method+"', '"+accept+"', 1)")
        subscriberid = c.lastrowid
        conn.commit()
        c.execute("insert into SensorEvent (data, subscriberid) values ('"+event+"', '"+str(subscriberid)+"')");
        result = c.lastrowid
        conn.commit()
        c.close()
        conn.close()
        return subscriberid

    def render_OPTIONS(self, request):
        request.setResponseCode(http.NO_CONTENT)
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, POST')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        logging.debug(request.requestHeaders)
        return ""

    def render_GET(self, request):
        """Handles GET requests. Shows the list of clients"""
        # TODO implement this
        self.data = self.datagen.next()
        dbclient = self.__getAllClients()
        #logging.debug("Client: ")
        #logging.debug(dbclient)
        # pprint(request.__dict__)
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        clients = ""
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, POST')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                for cl in dbclient:
                    clients += str('{"id":"%s", "uri":"%s", "method":"%s", "accept":"%s"}, ' % (cl[0], cl[1], cl[2], cl[3]))
                return str(
                    '{"clients": {"client":[%s]}}' % (clients[:-2]))
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                for cl in dbclient:
                    clients += str('<client><id>%s</id><uri>%s</uri><method>%s</method><accept>%s</accept></client> ' % (cl[0], cl[1], cl[2], cl[3]))
                return str(
                    '<clients>%s</clients>' % (clients))
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ClientsElement(dbclient)).addCallback(
                    request.write)
                request.finish()
                return NOT_DONE_YET

    def render_POST(self, request):
        """Handles POST request Add a client"""
        # TODO implement this
        #json_data = json.loads('{"uri": "192.168.2.1:4567", "accept":"application/json", "method":"POST"}')
        json_data = json.loads(request.content.getvalue())
        logging.debug(json_data)
        logging.debug(request.requestHeaders)
        accept_type = request.requestHeaders.getRawHeaders("Accept")[0]
        lastrowid = self.__insertClient(json_data['uri'], json_data['method'], json_data['accept'])
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'GET, POST')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours
        if not None:
            if accept_type == "application/json":
                request.setHeader("Content-Type", "application/json; charset=UTF-8")
                request.setResponseCode(200)
                return str('{"id":"%s", "uri":"%s", "method":"%s", "accept":"%s"}' % (lastrowid, json_data['uri'], json_data['method'], json_data['accept']))
            elif accept_type == "application/xml":
                request.setHeader("Content-Type", "application/xml; charset=UTF-8")
                request.setResponseCode(200)
                return str('<client><id>%s</id><uri>%s</uri><method>%s</method><accept>%s</accept></client>' % (lastrowid, json_data['uri'], json_data['method'], json_data['accept']))
            else:
                request.write("<!DOCTYPE html>\n")
                flattenString(request, ClientElement(lastrowid, json_data['uri'], json_data['method'], json_data['accept'], '')).addCallback(
                    request.write)
                request.finish()


    def getChild(self, name, request):
        """delegate to child resource"""
        if name == '':
            ServerFactory = HeartRateBroadcastFactory
            factory = ServerFactory("ws://localhost:"+str(self.__port)+"/", self.datagen, debug = False,  debugCodePaths = False)
            factory.protocol = wotStreamerProtocol
            factory.setProtocolOptions(allowHixie76 = True)
            return WebSocketResource(factory)
        else:
            return $child(self.datagen, name, self.__port, '')

