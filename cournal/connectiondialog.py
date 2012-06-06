#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# 
# Cournal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cournal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cournal.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk
from . import network

class ConnectionDialog(Gtk.Dialog):
    def __init__(self, parent, **args):
        Gtk.Dialog.__init__(self, **args)
        
        self.parent = parent
        
        builder = Gtk.Builder()
        builder.add_from_file("connection_dialog.glade")
        entry_grid = builder.get_object("grid_with_server_entry")
        self.server_entry = ServerPortEntry()
        self.multipage = builder.get_object("multipage")
        self.spinner = builder.get_object("spinner")
        self.error_label = builder.get_object("error_label")
        self.connecting_label = builder.get_object("connecting_label")
        
        self.get_content_area().add(builder.get_object("main_grid"))
        entry_grid.attach(self.server_entry, 1, 1, 1, 1)

        self.set_modal(False)
        self.set_has_resize_grip(False)
        self.set_resizable(False)
        self.set_title("Connect to Server")
        self.set_transient_for(parent)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_CONNECT, Gtk.ResponseType.ACCEPT)
        self.set_default_response(Gtk.ResponseType.ACCEPT)
        self.server_entry.set_activates_default(True)
        
        self.show_all()
    
    def response_cb(self, widget, response_id):
        if response_id != Gtk.ResponseType.ACCEPT:
            self.destroy()
            return
        
        server = self.server_entry.get_server()
        port = self.server_entry.get_port()
        
        if port > 65535 or port < 0:
            self.error_label.set_text("The port must be below 65535")
            self.error_label.show()
            return
        
        network.set_document(self.parent.document)
        d = network.connect(server, port)
        d.addCallbacks(self.on_connected, self.on_connection_failure)
        
        #FIXME: Display warning message, that the whole document goes bye-bye
        self.parent.document.clear_pages()
        
        self.multipage.set_current_page(1)
        self.spinner.start()
        self.error_label.set_text("")
        self.connecting_label.set_text("Connecting to {} ...".format(server))
        self.get_action_area().set_sensitive(False)
        
    def on_connected(self, perspective):
        self.destroy()
    
    def on_connection_failure(self, reason):
        error = reason.getErrorMessage()

        self.multipage.set_current_page(0)
        self.spinner.stop()
        self.error_label.set_text(error)
        self.error_label.show()
        self.get_action_area().set_sensitive(True)

    def run_nonblocking(self):
        self.connect('response', self.response_cb)
        self.show()

class ServerPortEntry(Gtk.EventBox):
    def __init__(self, **args):
        Gtk.EventBox.__init__(self, **args)
        
        frame = Gtk.Frame()
        server_port_align = Gtk.Box()
        self.server_entry = Gtk.Entry()
        colon_label = Gtk.Label()
        self.port_entry = Gtk.Entry()
        
        self.add(frame)
        frame.add(server_port_align)
        server_port_align.pack_start(self.server_entry, True, True, 0)
        server_port_align.pack_start(colon_label, False, False, 0)
        server_port_align.pack_start(self.port_entry, False, False, 0)
        
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255,255,255,255))
        frame.set_shadow_type(Gtk.ShadowType.IN)
        
        self.server_entry.set_has_frame(False)
        self.server_entry.set_text("127.0.0.1")
        self.server_entry.set_width_chars(20)
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

    def set_activates_default(self, setting):
        self.port_entry.set_activates_default(setting)
        self.server_entry.set_activates_default(setting)

    def get_server(self):
        return self.server_entry.get_text()
    
    def get_port(self):
        return int(self.port_entry.get_text())

# For testing purposes:
if __name__ == "__main__":
    dialog = ConnectionDialog(None)
    dialog.run()
