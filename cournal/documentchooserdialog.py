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

class DocumentChooserDialog(Gtk.Dialog):
    def __init__(self, parent, **args):
        Gtk.Dialog.__init__(self, **args)
        
        self.parent = parent
        
        self.selected = None
        
        builder = Gtk.Builder()
        builder.add_from_file("document_chooser_dialog.glade")

        self.doc_tree = builder.get_object("doc_tree")
        self.doc_tree_selection = builder.get_object("doc_tree_selection")
        self.doc_name = builder.get_object("doc_name")
        self.doc_tree_store = builder.get_object("doc_tree_store")
        self.doc_tree_column = builder.get_object("doc_tree_column")
        
        #help(self.doc_tree_view_column)
        
        self.doc_tree_selection.connect("changed", self.on_tree_select)
        
        self.get_content_area().add(builder.get_object("main_grid"))

        self.set_modal(False)
        self.set_has_resize_grip(False)
        self.set_resizable(True)
        self.set_title("Choose server document")
        self.set_transient_for(parent)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT)
        self.set_default_response(Gtk.ResponseType.ACCEPT)
        
        self.cell = Gtk.CellRendererText()
        self.doc_tree_column.pack_start(self.cell, True)
        self.doc_tree_column.add_attribute(self.cell, "text", 0)
        
        self.doc_tree_store.append(None, ["document1"])
        self.doc_tree_store.append(None, ["document2"])
        
        self.show_all()

    def on_tree_select(self, item):
        store, iter = item.get_selected()
        self.selected = store.get(iter,0)[0]
        self.doc_name.set_text(self.selected)
        print(self.selected)
        
    def run_nonblocking(self):
        self.connect('response', self.response_cb)
        self.show()

    def response_cb(self, widget, response_id):
        print(response_id)
        if response_id != Gtk.ResponseType.ACCEPT:
            self.destroy()
            return
        
        network.set_document(self.selected)
        
# For testing purposes:
if __name__ == "__main__":
    dialog = DocumentChooserDialog(None)
    dialog.run()
