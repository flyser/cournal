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

from .viewer import Layout
from . import Document, network, ConnectionDialog

class MainWindow(Gtk.Window):
    def __init__(self, **args):
        Gtk.Window.__init__(self, title="Cournal", **args)
        
        self.document = None
        
        self.set_default_size(width=500, height=700)
        
        # Bob the builder
        builder = Gtk.Builder()
        builder.add_from_file("mainwindow.glade")
        self.add(builder.get_object("outer_box"))
        
        # Initialize the main pdf viewer layout
        self.layout = None
        self.scrolledwindow = builder.get_object("scrolledwindow")
        
        # Menu Bar:
        self.open_pdf = builder.get_object("imagemenuitem_open_pdf")
        self.connectbutton = builder.get_object("imagemenuitem_connect")
        self.savebutton = builder.get_object("imagemenuitem_save")
        self.exportbutton = builder.get_object("imagemenuitem_export_pdf")

        self.savebutton.set_sensitive(False)
        self.exportbutton.set_sensitive(False)
        
        self.open_pdf.connect("activate", self.on_open_pdf_click)
        self.connectbutton.connect("activate", self.on_connect_click)
        self.savebutton.connect("activate", self.on_save_click)
        self.exportbutton.connect("activate", self.on_export_click)
    
    def on_open_pdf_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Open File", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            
            self.document = Document(filename)
            for child in self.scrolledwindow.get_children():
                self.scrolledwindow.remove(child)
            self.layout = Layout(self.document)
            self.scrolledwindow.add(self.layout)
            self.scrolledwindow.show_all()
            
            self.savebutton.set_sensitive(True)
            self.exportbutton.set_sensitive(True)

        dialog.destroy()
        
    def on_connect_click(self, menuitem):
        if not self.document:
            return
        dialog = ConnectionDialog(self)
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            server = dialog.get_server()
            port = dialog.get_port()
            
            network.set_document(self.document)
            network.connect(server, port)
            
        dialog.destroy()

    def on_save_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Save File", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_current_name("document.xoj")
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.save_xoj_file(filename)
        dialog.destroy()
    
    def on_export_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Export PDF", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_current_name("annotated_document.pdf")
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.export_pdf(filename)
        dialog.destroy()
        