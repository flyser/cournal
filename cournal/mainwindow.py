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
from .xojfilewriter import save_xoj_file

class MainWindow(Gtk.Window):
    def __init__(self, document, **args):
        Gtk.Window.__init__(self, **args)
        self.document = document
        
        self.set_default_size(width=500, height=700)
        
        # Bob the builder
        builder = Gtk.Builder()
        builder.add_from_file("mainwindow.glade")
        self.add(builder.get_object("outer_box"))
        
        # Initialize the main pdf viewer layout
        self.layout = Layout(self.document)
        builder.get_object("scrolledwindow").add(self.layout)
        
        # Save button:
        self.savebutton = builder.get_object("imagemenuitem_save")
        self.savebutton.connect("activate", self.on_savebutton_click)
        
    def on_savebutton_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Save File", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_current_name("document.xoj")
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            print("Saving to:", filename)
            save_xoj_file(self.document, filename)
        else:
            print("Not saving :-(")
        dialog.destroy()

        
