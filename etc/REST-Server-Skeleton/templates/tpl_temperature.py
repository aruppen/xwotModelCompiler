from twisted.web.template import Element, renderer, XMLFile,  XMLString
from twisted.python.filepath import FilePath

class ExampleElement(Element):
    loader = XMLFile(FilePath('templates/tpl_temperature.xml'))

    
    def __init__(self, temp,  hum):
        self.temperature = temp
        self.hummidity = hum
        self.extraTemperatureContent = XMLString('<input id="temperature" type="range" min="-100" max="100" value="'+self.temperature+'" class="xwot sensor columns large-8" />')
        self.extraHumidityContent = XMLString('<input id="humidity" type="range" min="0" max="100" value="'+self.hummidity+'" class="xwot sensor columns large-8" />')

    @renderer
    def header(self, request, tag):
        return tag('Header.')
        
    @renderer
    def temp(self, request, tag):
        return self.temperature
        
    @renderer
    def temperatureInput(self,  request,  tag):
        return self.extraTemperatureContent.load()

    @renderer
    def humidity(self, request, tag):
        return self.hummidity
        
    @renderer
    def humidityInput(self,  request,  tag):
        return self.extraHumidityContent.load()
