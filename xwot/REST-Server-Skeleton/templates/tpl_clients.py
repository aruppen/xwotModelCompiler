from twisted.web.template import Element, TagLoader, renderer, XMLFile,  XMLString
from twisted.python.filepath import FilePath

class ClientsElement(Element):
    loader = XMLFile(FilePath('templates/tpl_clients.xml'))
    widgetData = [(2, u'http://example2.com/notif', u'POST', u'application/xml', 1), (1, u'http://example.com/notif', u'POST', u'application/xml', 1), (3, u'http://example3.com/notif', u'POST', u'application/xml', 1)]#['gadget', 'contraption', 'gizmo', 'doohickey']
    def __init__(self, clients):
        self.clients = clients

    @renderer
    def header(self, request, tag):
        return tag('Header.')

    @renderer
    def myclients(self, request, tag):
        for widget in self.clients:
            #yield tag.clone().fillSlots(uri=str(widget[0]))
            clonedtag = tag.clone()
            clonedtag.fillSlots(id=str(widget[0]))
            clonedtag.fillSlots(uri=str(widget[1]))
            clonedtag.fillSlots(method=str(widget[2]))
            clonedtag.fillSlots(accept=str(widget[3]))
            yield clonedtag

    @renderer
    def widgets(self, request, tag):
        for widget in self.widgetData:
            yield tag.clone().fillSlots(widgetName=widget[1])
