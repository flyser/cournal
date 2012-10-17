#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# Copyright (C) 2012 Simon Vetter
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

import os.path
from gi.repository import Gtk, GObject

import cournal
from cournal.network import network

class DocumentChooser(Gtk.Box):
    """
    A widget, which allows the user to browse and open remote documents.
    """
    __gsignals__ = {
        "got_document_list": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "joining_document": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        "joined_document": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, dialog):
        """
        Constructor.
        
        Positional arguments:
        dialog -- The parent GtkDialog widget.
        """
        Gtk.Box.__init__(self)
        self.selected = None
        self.deferred = None
        self.dialog = dialog
        
        builder = Gtk.Builder()
        builder.set_translation_domain("cournal")
        builder.add_from_file(os.path.join(cournal.__path__[0], "document_chooser.glade"))
        self.main_grid = builder.get_object("main_grid")
        
        self.doc_tree = builder.get_object("tree_view_documents")
        self.doc_tree_selection = builder.get_object("tree_selection_documents")
        self.doc_name = builder.get_object("entry_document_name")
        self.doc_tree_store = builder.get_object("tree_store_documents")
        self.doc_tree_column = builder.get_object("tree_view_column_documents")
        
        self.cell = Gtk.CellRendererText()
        self.doc_tree_column.pack_start(self.cell, True)
        self.doc_tree_column.add_attribute(self.cell, "text", 0)
        self.doc_tree_store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        
        self.doc_tree_selection.connect("changed", self.on_tree_select)
        self.connect("map", self.on_map_event)
    
    def response(self, widget, response_id):
        """
        Called, when the user clicked on a button ('Connect' or 'Abort') or
        when the dialog is closed.
        If the user clicked on connect, we join a document session.
        
        Positional arguments:
        widget -- The widget, which triggered the response.
        response_id -- A Gtk.ResponseType indicating, which button the user pressed.
        """
        if response_id == Gtk.ResponseType.ACCEPT:
            documentname = self.doc_name.get_text()
            self.deferred = network.join_document_session(documentname)
            self.deferred.addCallback(self.joined_document)
            self.emit("joining_document", documentname)
        else:
            network.disconnect()
            self.dialog.destroy()
    
    def joined_document(self, _):
        """Called, when we got the remote document from the server"""
        self.emit("joined_document")
    
    def on_map_event(self, _):
        """
        Called, when the widget becomes visible.
        As this widget is so large, that all previous pages would look ugly, we
        add ourselves to the layout only when becoming visible.
        """
        if len(self.get_children()) == 0:
            self.add(self.main_grid)
            self.show_all()

    def get_document_list(self):
        """Get the list of all remote documents from the server."""
        d = network.get_document_list()
        d.addCallback(self.got_document_list)
        return d
    
    def got_document_list(self, documents):
        """
        Called, when we got the remote document list from the server.
        
        Positional arguments:
        documents -- the list of documents
        """
        self.doc_tree_store.clear()
        for i in documents:
            self.doc_tree_store.append(None, [i])
        
        if len(documents) > 0:
            self.doc_name.set_text(documents[0])
        else:
            self.doc_name.set_text(_("New document"))
        
        self.emit("got_document_list")

    def on_tree_select(self, item):
        """Called, when the user clicked on an item in the document selector."""
        store, iter = item.get_selected()
        if iter:
            self.selected = store.get(iter, 0)[0]
            self.doc_name.set_text(self.selected)
