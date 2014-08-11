import logging
import logging.config
import pybonjour


class ZeroconfService:
    """A simple class witch publishes the actual service with avahi"""

    def __init__(self, name, port, stype="_wot._tcp", subtype="_sensor", domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.subtype = subtype + "._sub." + stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text
        self.serviceDef = None

    def register_callback(self, sdRef, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            logging.debug('Registered service:')
            logging.debug('  name    =' + name)
            logging.debug('  regtype =' + regtype)
            logging.debug('  domain  =' + domain)

    def publish(self):
        #txt = {'model': 'RackMac', 'room': 'C412'}
        avahitxt = pybonjour.TXTRecord(self.text, strict=True)
        self.serviceDef = pybonjour.DNSServiceRegister(name=self.name,
                                                       regtype=self.stype,
                                                       port=self.port,
                                                       txtRecord=avahitxt,
                                                       callBack=self.register_callback)

    def unpublish(self):
        self.serviceDef.close()
