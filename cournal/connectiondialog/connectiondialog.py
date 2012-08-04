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

from gi.repository import Gtk

import cournal
from cournal.connectiondialog.serverdetails import ServerDetails
from cournal.connectiondialog.connectingpage import ConnectingPage
from cournal.connectiondialog.documentchooser import DocumentChooser

class ConnectionDialog(Gtk.Dialog):
    """
    The "Connect to Server" dialog of Cournal.
    """
    def __init__(self, parent):
        """
        Constructor.
        
        Positional arguments:
        parent -- Parent window of this dialog
        """
        Gtk.Dialog.__init__(self)
        self.parent = parent
        
        builder = Gtk.Builder()
        builder.set_translation_domain("cournal")
        builder.add_from_file(cournal.__path__[0] + "/connection_dialog.glade")
        grid = builder.get_object("grid_main")
        
        self.multipage = builder.get_object("multipage")
        self.error_label = builder.get_object("error_label")
        self.server_details = ServerDetails(self, builder)
        self.connecting_page = ConnectingPage(self, builder)
        self.document_chooser = DocumentChooser(self)
        
        self.get_content_area().add(grid)
        self.multipage.append_page(self.server_details, None)
        self.multipage.append_page(self.connecting_page, None)
        self.multipage.append_page(self.document_chooser, None)
        
        self.set_modal(False)
        self.set_has_resize_grip(False)
        self.set_resizable(False)
        self.set_title(_("Connect to Server"))
        self.set_transient_for(parent)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_CONNECT, Gtk.ResponseType.ACCEPT)
        self.set_default_response(Gtk.ResponseType.ACCEPT)
        
        self.set_page(0)
        
        self.connect("response", self.response)
        self.server_details.connect("connecting", self.show_connecting_page)
        self.server_details.connect("connected", lambda x: self.document_chooser.get_document_list())
        self.server_details.connect("connection_failed", lambda x: self.set_page(0))
        self.document_chooser.connect("got_document_list", lambda x: self.set_page(2))
        self.document_chooser.connect("joining_document", self.show_joining_document_page)
        self.document_chooser.connect("joined_document", lambda x: self.destroy())
    
    def show_connecting_page(self, widget, server, port):
        """
        Show a widget indicating, that a connection is being established.
        
        Positional arguments:
        widget -- The previously active widget (normally server_details)
        server -- The hostname of the server we are connecting to
        port -- Port number on the server
        """
        self.set_page(1)
        self.connecting_page.message = _("Connecting to {} ...").format(server)
        self.connecting_page.deferred = widget.deferred
        
    def show_joining_document_page(self, widget, documentname):
        """
        Show a widget, indicating that a remote document is being opened.
        
        Positional arguments:
        widget -- The previously active widget (normally document_chooser)
        documentname -- The name of the document we are opening
        """
        self.set_page(1)
        self.connecting_page.message = _("Opening {} ...").format(documentname)
        self.connecting_page.deferred = widget.deferred
    
    def set_page(self, page):
        """
        Switch to a given page in our multipage widget containing the
        server_details, connecting_page and the document_chooser widget.
        
        Positional arguments:
        page -- Number of the page to switch to. Starting from 0.
        """
        if page == 1:
            self.get_action_area().set_sensitive(False)
        else:
            self.get_action_area().set_sensitive(True)
        self.multipage.set_current_page(page)
        self.multipage.get_nth_page(page)
        self.current_page = self.multipage.get_nth_page(page)
    
    def response(self, widget, response_id):
        """
        Called, when the user clicked on a button ('Connect' or 'Abort') or
        when the dialog is closed.
        
        Positional arguments:
        widget -- The widget, which triggered the response.
        response_id -- A Gtk.ResponseType indicating, which button the user pressed.
        """
        self.current_page.response(widget, response_id)
    
    @property
    def error(self):
        """The error message to display"""
        return self.error_label.get_text()
    
    @error.setter
    def error(self, message):
        self.error_label.set_text(message)
        if message and message != "" :
            self.error_label.show()
    
    def run_nonblocking(self):
        """Run the dialog asynchronously, reusing the mainloop of the parent."""
        self.show_all()

# For testing purposes:
if __name__ == "__main__":
    dialog = ConnectionDialog(None)
    dialog.run()
