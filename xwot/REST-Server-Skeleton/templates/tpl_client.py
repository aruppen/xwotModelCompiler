__author__ = 'ruppena'
from twisted.web.template import Element, renderer, XMLFile,  XMLString
from twisted.python.filepath import FilePath

class ClientElement(Element):
    loader = XMLFile(FilePath('templates/tpl_client.xml'))


    def __init__(self, _id,  _url, _method, _accpettype, _data):
        self.id = _id
        self.url = _url
        self.accept = _accpettype
        self.method = _method
        self.data = _data



    @renderer
    def header(self, request, tag):
        return tag('Header.')

    @renderer
    def clientid(self, request, tag):
        return str(self.id)

    @renderer
    def clienturl(self, request, tag):
        return self.url

    @renderer
    def clientaccept(self, request, tag):
        return self.accept

    @renderer
    def clientmethod(self, request, tag):
        return self.method

    @renderer
    def clientdata(self, request, tag):
        return self.data


