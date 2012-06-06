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
from gi.repository.GLib import GError

from .viewer import Layout
from . import Document, ConnectionDialog, AboutDialog

class MainWindow(Gtk.Window):
    def __init__(self, **args):
        Gtk.Window.__init__(self, title="Cournal", **args)
        
        self.document = None
        self.filename = None
        
        self.set_default_size(width=500, height=700)
        self.set_icon_name("cournal")
        
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
        self.saveasbutton = builder.get_object("imagemenuitem_save_as")
        self.exportbutton = builder.get_object("imagemenuitem_export_pdf")
        self.aboutbutton = builder.get_object("imagemenuitem_about")
        self.quitbutton = builder.get_object("imagemenuitem_quit")

        self.connectbutton.set_sensitive(False)
        self.savebutton.set_sensitive(False)
        self.saveasbutton.set_sensitive(False)
        self.exportbutton.set_sensitive(False)
        
        self.open_pdf.connect("activate", self.on_open_pdf_click)
        self.connectbutton.connect("activate", self.on_connect_click)
        self.savebutton.connect("activate", self.on_save_click)
        self.saveasbutton.connect("activate", self.on_save_as_click)
        self.exportbutton.connect("activate", self.on_export_click)
        self.aboutbutton.connect("activate", self.on_about_click)
        self.quitbutton.connect("activate", lambda _: self.destroy())
        
        # Tool Bar:
        self.open_pdftool = builder.get_object("tool_open_pdf")
        self.connecttool = builder.get_object("tool_connect")
        self.savetool = builder.get_object("tool_save")
        self.zoom_in_tool = builder.get_object("tool_zoom_in")
        self.zoom_out_tool = builder.get_object("tool_zoom_out")
        self.zoom_100_tool = builder.get_object("tool_zoom_100")
        self.pen_color_tool = builder.get_object("tool_pen_color")

        self.connecttool.set_sensitive(False)
        self.pen_color_tool.set_sensitive(False)
        self.savetool.set_sensitive(False)
        self.zoom_100_tool.set_sensitive(False)
        self.zoom_in_tool.set_sensitive(False)
        self.zoom_out_tool.set_sensitive(False)
        
        self.open_pdftool.connect("clicked", self.on_open_pdf_click)
        self.connecttool.connect("clicked", self.on_connect_click)
        self.savetool.connect("clicked", self.on_save_click)
        self.zoom_in_tool.connect("clicked", self.on_zoom_in_click)
        self.zoom_out_tool.connect("clicked", self.on_zoom_out_click)
        self.zoom_100_tool.connect("clicked", self.on_zoom_100_click)
        self.pen_color_tool.connect("color-set", self.on_pen_color_change)
    
    def on_open_pdf_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Open File", self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        pdf_filter = Gtk.FileFilter()
        pdf_filter.add_mime_type("application/pdf")
        dialog.set_filter(pdf_filter)
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            
            try:
                document = Document(filename)
            except GError as ex:
                message = Gtk.MessageDialog(self, (Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT), Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Unable to open PDF" )
                message.format_secondary_text(ex)
                message.set_title("Error")
                message.connect("response", lambda _,x: message.destroy())
                message.show()
                print("Unable to open PDF file:", ex)
                dialog.destroy()
                return
            
            self.document = document
            for child in self.scrolledwindow.get_children():
                self.scrolledwindow.remove(child)
            self.layout = Layout(self.document)
            self.scrolledwindow.add(self.layout)
            self.scrolledwindow.show_all()
            
            self.connectbutton.set_sensitive(True)
            self.savebutton.set_sensitive(True)
            self.saveasbutton.set_sensitive(True)
            self.exportbutton.set_sensitive(True)
            self.connecttool.set_sensitive(True)
            self.zoom_100_tool.set_sensitive(True)
            self.zoom_in_tool.set_sensitive(True)
            self.zoom_out_tool.set_sensitive(True)
            self.savetool.set_sensitive(True)

        dialog.destroy()
        
    def on_connect_click(self, menuitem):
        # Need to hold a reference, so the object does not get garbage collected
        self._connection_dialog = ConnectionDialog(self)
        self._connection_dialog.connect("destroy", self.connection_dialog_destroyed)
        self._connection_dialog.run_nonblocking()

    def on_save_click(self, menuitem):
        if self.filename:
            self.document.save_xoj_file(self.filename)
        else:
            self.on_save_as_click(menuitem)

    def on_save_as_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Save File As", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_current_name("document.xoj")
        
        pdf_filter = Gtk.FileFilter()
        pdf_filter.add_mime_type("application/x-xoj")
        dialog.set_filter(pdf_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.save_xoj_file(filename)
            self.filename = filename
            self.set_title("cournal - "+filename)
        dialog.destroy()
    
    def on_export_click(self, menuitem):
        dialog = Gtk.FileChooserDialog("Export PDF", self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_current_name("annotated_document.pdf")
        
        pdf_filter = Gtk.FileFilter()
        pdf_filter.add_mime_type("application/pdf")
        dialog.set_filter(pdf_filter)
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.export_pdf(filename)
        dialog.destroy()
        
    def on_about_click(self, menuitem):
        # Need to hold a reference, so the object does not get garbage collected
        self._about_dialog = AboutDialog(self)
        self._about_dialog.connect("destroy", self.about_dialog_destroyed)
        self._about_dialog.run_nonblocking()

    def on_pen_color_change(self, menuitem):
        #TODO: Change Stroke Color
        print(menuitem.get_color())

    def on_zoom_in_click(self, menuitem):
        self.layout.set_zoom(change=0.2)

    def on_zoom_out_click(self, menuitem):
        self.layout.set_zoom(change=-0.2)
    
    def on_zoom_100_click(self, menuitem):
        self.layout.set_zoom(1)
        
    def about_dialog_destroyed(self, widget):
        self._about_dialog = None
        
    def connection_dialog_destroyed(self, widget):
        self._connection_dialog = None
        
        
