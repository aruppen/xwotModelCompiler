import avahi
import dbus

class ZeroconfService:
    """A simple class witch publishes the actual service with avahi"""
    
    """Courtesy of http://stackoverflow.com/questions/3430245/how-to-develop-an-avahi-client-server"""
    
    def __init__(self,  name,  port, stype="_wot._tcp", subtype="_sensor",  domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.subtype = subtype+"._sub."+stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text
        
    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), avahi.string_array_to_txt_array(self.text))
        g.AddServiceSubtype(avahi.IF_UNSPEC,  avahi.PROTO_UNSPEC,  dbus.UInt32(0), self.name,  self.stype,  self.domain,  self.subtype)

        g.Commit()
        self.group = g
    
    def unpublish(self):
        self.group.Reset()
        
