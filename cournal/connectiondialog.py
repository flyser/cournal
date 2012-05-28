
from gi.repository import Gtk, Gdk

class ConnectionDialog(Gtk.Dialog):
    def __init__(self, parent, **args):
        Gtk.Dialog.__init__(self, **args)
        
        self.content_area = self.get_content_area()
        grid = Gtk.Grid()
        self.server_port_entry = ServerPortEntry()
        image = Gtk.Image()
        label = Gtk.Label()
        smalllabel = Gtk.Label()

        self.content_area.add(grid)
        grid.attach(image, 0, 0, 1, 3)
        grid.attach(self.server_port_entry, 2, 1, 1, 1)
        grid.attach(label, 1, 0, 2, 1)
        grid.attach(smalllabel, 1, 1, 1, 1)
        
        self.set_has_resize_grip(False)
        self.set_modal(True)
        self.set_title("Connect to Server")
        self.set_transient_for(parent)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_CONNECT, Gtk.ResponseType.ACCEPT)
        image.set_from_stock(Gtk.STOCK_NETWORK, Gtk.IconSize.DIALOG)
        label.set_text("Please enter the Name and port of the server, you want to connect to.")
        smalllabel.set_text("Server name:")
        self.show_all()
    
    def get_server(self):
        return self.server_port_entry.get_server()
    def get_port(self):
        return self.server_port_entry.get_port()

class ServerPortEntry(Gtk.EventBox):
    def __init__(self, **args):
        Gtk.EventBox.__init__(self, **args)
        
        frame = Gtk.Frame()
        server_port_align = Gtk.HBox()
        self.server_entry = Gtk.Entry()
        colon_label = Gtk.Label()
        self.port_entry = Gtk.Entry()
        
        self.add(frame)
        frame.add(server_port_align)
        server_port_align.add(self.server_entry)
        server_port_align.add(colon_label)
        server_port_align.add(self.port_entry)
        
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255,255,255,255))
        frame.set_shadow_type(Gtk.ShadowType.IN)
        
        self.server_entry.set_has_frame(False)
        self.server_entry.set_text("127.0.0.1")
        colon_label.set_text(":")
        self.port_entry.set_has_frame(False)
        self.port_entry.set_max_length(5)
        self.port_entry.set_width_chars(5)
        self.port_entry.set_text("6524")
        
        self.port_entry.connect("insert_text", self.port_entry_updated)

    def port_entry_updated(self, widget, text, length, position):
        if not text.isdigit():
            widget.emit_stop_by_name("insert_text")
            return

    def get_server(self):
        return self.server_entry.get_text()
    
    def get_port(self):
        return int(self.port_entry.get_text())
