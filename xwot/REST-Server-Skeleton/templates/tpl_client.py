from twisted.web.template import Element, renderer, XMLFile,  XMLString
from twisted.python.filepath import FilePath

class ClientElement(Element):
    loader = XMLFile(FilePath('templates/tpl_client.xml'))

    
    def __init__(self, id, url, method, accept):
        self.id = str(id)
        self.url = url
        self.method = method
        self.accept = accept


    @renderer
    def header(self, request, tag):
        return tag('Header.')

    @renderer
    def idContent(self, request, tag):
        return self.id


    @renderer
    def uriContent(self, request, tag):
        return self.url

    @renderer
    def methodContent(self, request, tag):
        return self.method

    @renderer
    def acceptContent(self, request, tag):
        return self.accept


