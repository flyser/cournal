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

from time import time

from gi.repository import Gtk, Gdk, GObject
from gi.repository.GLib import GError

import cournal
from cournal.viewer.layout import Layout
from cournal.viewer.tools import pen
from cournal.document.document import Document
from cournal.document import xojparser
from cournal.network import network
from cournal.connectiondialog.connectiondialog import ConnectionDialog
from cournal.aboutdialog import AboutDialog

pdf_filter = Gtk.FileFilter()
pdf_filter.add_mime_type("application/pdf")
xoj_filter = Gtk.FileFilter()
xoj_filter.add_mime_type("application/x-xoj")

LINEWIDTH_SMALL = 0.7
LINEWIDTH_NORMAL = 1.5
LINEWIDTH_BIG = 8.0

class MainWindow(Gtk.Window):
    """
    Cournals main window
    """
    def __init__(self, **args):
        """
        Constructor.
        
        Keyword arguments:
        **args -- Arguments passed to the Gtk.Window constructor
        """
        Gtk.Window.__init__(self, title=_("Cournal"), **args)
        network.set_window(self)
        
        self.overlaybox = None
        self.document = None
        self.last_filename = None
        
        self.set_default_size(width=500, height=700)
        self.set_icon_name("cournal")
        
        # Bob the builder
        builder = Gtk.Builder()
        builder.set_translation_domain("cournal")
        builder.add_from_file(cournal.__path__[0] + "/mainwindow.glade")
        self.add(builder.get_object("outer_box"))
        
        # Initialize the main journal layout
        self.layout = None
        self.overlay = builder.get_object("overlay")
        self.scrolledwindow = builder.get_object("scrolledwindow")
        
        # Menu Bar:
        self.menu_open_xoj = builder.get_object("imagemenuitem_open_xoj")
        self.menu_open_pdf = builder.get_object("imagemenuitem_open_pdf")
        self.menu_connect = builder.get_object("imagemenuitem_connect")
        self.menu_save = builder.get_object("imagemenuitem_save")
        self.menu_save_as = builder.get_object("imagemenuitem_save_as")
        self.menu_export_pdf = builder.get_object("imagemenuitem_export_pdf")
        self.menu_import_xoj = builder.get_object("imagemenuitem_import_xoj")
        self.menu_quit = builder.get_object("imagemenuitem_quit")
        self.menu_about = builder.get_object("imagemenuitem_about")
        
        # Toolbar:
        self.tool_open_pdf = builder.get_object("tool_open_pdf")
        self.tool_save = builder.get_object("tool_save")
        self.tool_connect = builder.get_object("tool_connect")
        self.tool_zoom_in = builder.get_object("tool_zoom_in")
        self.tool_zoom_out = builder.get_object("tool_zoom_out")
        self.tool_zoom_100 = builder.get_object("tool_zoom_100")
        self.tool_pen_color = builder.get_object("tool_pen_color")
        self.tool_pensize_small = builder.get_object("tool_pensize_small")
        self.tool_pensize_normal = builder.get_object("tool_pensize_normal")
        self.tool_pensize_big = builder.get_object("tool_pensize_big")

        self.menu_connect.set_sensitive(False)
        self.menu_save.set_sensitive(False)
        self.menu_save_as.set_sensitive(False)
        self.menu_export_pdf.set_sensitive(False)
        self.menu_import_xoj.set_sensitive(False)
        self.tool_save.set_sensitive(False)
        self.tool_connect.set_sensitive(False)
        self.tool_zoom_in.set_sensitive(False)
        self.tool_zoom_out.set_sensitive(False)
        self.tool_zoom_100.set_sensitive(False)
        self.tool_pen_color.set_sensitive(False)
        self.tool_pensize_small.set_sensitive(False)
        self.tool_pensize_normal.set_sensitive(False)
        self.tool_pensize_big.set_sensitive(False)
        
        self.menu_open_xoj.connect("activate", self.run_open_xoj_dialog)
        self.menu_open_pdf.connect("activate", self.run_open_pdf_dialog)
        self.menu_connect.connect("activate", self.run_connection_dialog)
        self.menu_save.connect("activate", self.save)
        self.menu_save_as.connect("activate", self.run_save_as_dialog)
        self.menu_export_pdf.connect("activate", self.run_export_pdf_dialog)
        self.menu_import_xoj.connect("activate", self.run_import_xoj_dialog)
        self.menu_quit.connect("activate", lambda _: self.destroy())
        self.menu_about.connect("activate", self.run_about_dialog)
        self.tool_open_pdf.connect("clicked", self.run_open_pdf_dialog)
        self.tool_save.connect("clicked", self.save)
        self.tool_connect.connect("clicked", self.run_connection_dialog)
        self.tool_zoom_in.connect("clicked", self.zoom_in)
        self.tool_zoom_out.connect("clicked", self.zoom_out)
        self.tool_zoom_100.connect("clicked", self.zoom_100)
        self.tool_pen_color.connect("color-set", self.change_pen_color)
        self.tool_pensize_small.connect("clicked", self.change_pen_size, LINEWIDTH_SMALL)
        self.tool_pensize_normal.connect("clicked", self.change_pen_size, LINEWIDTH_NORMAL)
        self.tool_pensize_big.connect("clicked", self.change_pen_size, LINEWIDTH_BIG)
    
        # Statusbar:
        self.statusbar_icon = builder.get_object("image_statusbar")
        self.statusbar_pagenum = builder.get_object("label_statusbar_center")
        self.statusbar_pagenum_entry = builder.get_object("entry_statusbar_page_num")
        self.button_prev_page = builder.get_object("btn_prev_page")
        self.button_next_page = builder.get_object("btn_next_page")
        self.vadjustment = self.scrolledwindow.get_vadjustment()
        self.vadjustment.connect("value_changed", self.show_page_numbers)
        self.statusbar_pagenum_entry.connect("insert-text", self.jump_to_page_control)
        self.statusbar_pagenum_entry.connect("activate", self.jump_to_page)
        self.button_prev_page.connect("clicked", self.jump_to_prev_page)
        self.button_next_page.connect("clicked", self.jump_to_next_page)

    def connect_event(self):
        """
        Called by the networking layer when a connection is established.
        Set the statusbar icon accordingly.
        """
        self.statusbar_icon.set_from_stock(Gtk.STOCK_CONNECT, Gtk.IconSize.SMALL_TOOLBAR)

    def disconnect_event(self):
        """
        Called by the networking code, when we get disconnected from the server.
        """
        self.statusbar_icon.set_from_stock(Gtk.STOCK_DISCONNECT, Gtk.IconSize.SMALL_TOOLBAR)
    
    def connection_problems(self):
        """
        Called by the networking code, when the server did not respond for
        some time or when we are disconnected.
        """
        def destroyed(widget):
            self.overlaybox = None
            # Do we run on Gtk 3.2?
            if Gtk.check_version(3,4,0) != None: self.overlay.add(self.scrolledwindow)

        if self.overlaybox is not None:
            return
        
        self.overlaybox = OverlayDialog()
        # GtkOverlay is broken in Gtk 3.2, so we apply a workaround:
        if Gtk.check_version(3,4,0) == None:
            # Gtk 3.4+
            self.overlay.add_overlay(self.overlaybox)
        else:
            # Gtk 3.2
            if self.overlay.get_child() == self.scrolledwindow:
                self.overlay.remove(self.scrolledwindow)
            self.overlay.add(self.overlaybox)
        self.overlaybox.connect("destroy", destroyed)
    
    def _set_document(self, document):
        """
        Replace the current document (if any) with a new one.
        
        Positional arguments:
        document -- The new Document object.
        """
        self.document = document
        for child in self.scrolledwindow.get_children():
            self.scrolledwindow.remove(child)
        self.layout = Layout(self.document)
        self.scrolledwindow.add(self.layout)
        self.scrolledwindow.show_all()
        self.last_filename = None
        
        self.menu_connect.set_sensitive(True)
        self.menu_save.set_sensitive(True)
        self.menu_save_as.set_sensitive(True)
        self.menu_export_pdf.set_sensitive(True)
        self.menu_import_xoj.set_sensitive(True)
        self.tool_save.set_sensitive(True)
        self.tool_connect.set_sensitive(True)
        self.tool_zoom_in.set_sensitive(True)
        self.tool_zoom_out.set_sensitive(True)
        self.tool_zoom_100.set_sensitive(True)
        self.tool_pen_color.set_sensitive(True)
        self.tool_pensize_small.set_sensitive(True)
        self.tool_pensize_normal.set_sensitive(True)
        self.tool_pensize_big.set_sensitive(True)
        self.statusbar_pagenum.set_sensitive(True)
        self.statusbar_pagenum_entry.set_sensitive(True)
        
        if self.document.num_of_pages > 1:
            self.button_next_page.set_sensitive(True)
        
        # at this point we always start at page 1. If the feature to resume last page is included
        # remove this and start the method show_page_numbers() with adjustment
        self.statusbar_pagenum.set_text(_(" of {:3}").format(self.document.num_of_pages))
        self.curr_page = 1
        self.statusbar_pagenum_entry.set_text(str(self.curr_page))

        # Hide the disconnection overlay dialog when the user opens a new doc
        if self.overlaybox:
            self.overlaybox.destroy()
    
    def show_page_numbers(self, curr_vadjustment):
        """
        Show current and absolute Page number in the center of the Statusbar.
        To achive that the current visible window and page size are compared if there is a intersection.
        If so and more than 60% of the new page are shown the current shown page number is updatet.

        Positional Arguments:
        curr_vadjustemnt - current vertical adjustment of the scrollbar
        """
        biggest_intersection = [0,0]
 
        for page in self.document.pages:
            rectangle = Gdk.Rectangle()
            intersection = Gdk.Rectangle()
            # horizontal adjustment is always 0, because the horizontal adjustment does not matter
            rectangle.x = 0
            rectangle.y = curr_vadjustment.get_value() 
            rectangle.height = self.layout.get_allocation().height 
            rectangle.width = self.layout.get_allocation().width
            # calculation should work in most cases (visible pages <= 3)
            intersect = page.widget.intersect(rectangle, intersection)
            if intersect and (intersection.height > page.widget.get_allocated_height() * 0.6):
                self.curr_page = page.number + 1
                self.statusbar_pagenum_entry.set_text(str(self.curr_page))
                self.update_button_sensitivity()
                return
            if intersection.height > biggest_intersection[0]:
                biggest_intersection[0] = intersection.height
                biggest_intersection[1] = page.number + 1
        # fallback if no page has a overall visibility of more than 60%. In this case the page with the highest visibility is choosen
        self.curr_page = biggest_intersection[1]
        self.statusbar_pagenum_entry.set_text(str(self.curr_page))
        self.update_button_sensitivity()

    def update_button_sensitivity(self):
        """
        Sensitivity of buttons is set / unset if a specific page is reached.
        """
        if self.curr_page == 1:
            self.button_prev_page.set_sensitive(False)
        else:
            self.button_prev_page.set_sensitive(True)
        
        if self.curr_page == self.document.num_of_pages:
            self.button_next_page.set_sensitive(False)
        else:
            self.button_next_page.set_sensitive(True)

    def jump_to_page_control(self, page_num, text, length, position):
        """
        Checks if only valid data is inserted.
        Called each time the user changes the page number entry.

        Positional arguments: (see GtkEditable "insert-text" documentation)
        widget -- The widget that was updated.
        text -- The text to append.
        length -- The length of the text in bytes, or -1.
        position -- Location of the position text will be inserted at as gpointer.
        """
        position = page_num.get_position()
        old_text = page_num.get_text()
        try:
            insert_num = int(old_text[:position] + text + old_text[position:])
        except:
            page_num.emit_stop_by_name("insert_text")
        if not text.isdigit() or insert_num > self.document.num_of_pages or insert_num == 0:
            page_num.emit_stop_by_name("insert_text")
        
    def jump_to_page(self, page_num_widget):
        """
        Sets the vertical adjustment of the scrollbar to the page the user wishes to jump to.
        Called each time the page number entry is updated.

        Positional arguments:
        page_num_widget: The Entry widget that was updated.
        """
        for page in self.document.pages:
            if page.number + 1 == int(page_num_widget.get_text()):
                self.vadjustment.set_value(page.widget.get_allocation().y)
                return
    
    def jump_to_next_page(self, menuitem):
        """
        Jump to the next page
        called each time the button_next_page is pressed
        """
        self.statusbar_pagenum_entry.set_text(str(self.curr_page + 1)) 
        self.statusbar_pagenum_entry.activate()

    def jump_to_prev_page(self, menuitem):
        """
        Jump to the previous page
        called each time the button_prev_page is pressed
        """
        self.statusbar_pagenum_entry.set_text(str(self.curr_page - 1)) 
        self.statusbar_pagenum_entry.activate()
    
    def run_open_pdf_dialog(self, menuitem):
        """
        Run an "Open PDF" dialog and create a new document with that PDF.
        """
        dialog = Gtk.FileChooserDialog(_("Open File"), self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(pdf_filter)
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            
            try:
                document = Document(filename)
            except GError as ex:
                self.run_error_dialog(_("Unable to open PDF"), ex)
                dialog.destroy()
                return
            self._set_document(document)
        dialog.destroy()
    
    def run_connection_dialog(self, menuitem):
        """
        Run a "Connect to Server" dialog.
        """
        def destroyed(widget):
            self._connection_dialog = None
        # Need to hold a reference, so the object does not get garbage collected
        self._connection_dialog = ConnectionDialog(self)
        self._connection_dialog.connect("destroy", destroyed)
        self._connection_dialog.run_nonblocking()
        
    def run_import_xoj_dialog(self, menuitem):
        """
        Run an "Import .xoj" dialog and import the strokes.
        """
        dialog = Gtk.FileChooserDialog(_("Open File"), self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(xoj_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            xojparser.import_into_document(self.document, filename, self)
        dialog.destroy()
    
    def run_open_xoj_dialog(self, menuitem):
        """
        Run an "Open .xoj" dialog and create a new document from a .xoj file.
        """
        dialog = Gtk.FileChooserDialog(_("Open File"), self, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(xoj_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            try:
                document = xojparser.new_document(filename, self)
            except Exception as ex:
                print(ex)
                dialog.destroy()
                return
            self._set_document(document)
            self.last_filename = filename
        dialog.destroy()

    def save(self, menuitem):
        """
        Save document to the last known filename or ask the user for a location.
        
        Positional arguments:
        menuitem -- The menu item, that triggered this function
        """
        if self.last_filename:
            self.document.save_xoj_file(self.last_filename)
        else:
            self.run_save_as_dialog(menuitem)
    
    def run_save_as_dialog(self, menuitem):
        """
        Run a "Save as" dialog and save the document to a .xoj file
        """
        dialog = Gtk.FileChooserDialog(_("Save File As"), self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(xoj_filter)
        dialog.set_current_name("document.xoj")

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.save_xoj_file(filename)
            self.last_filename = filename
        dialog.destroy()

    def run_export_pdf_dialog(self, menuitem):
        """
        Run an "Export" dialog and save the document to a PDF file.
        """
        dialog = Gtk.FileChooserDialog(_("Export PDF"), self, Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT,
                                        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        dialog.set_filter(pdf_filter)
        dialog.set_current_name("annotated_document.pdf")
        
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            self.document.export_pdf(filename)
        dialog.destroy()
        
    def run_about_dialog(self, menuitem):
        """
        Run the "About" dialog.
        """
        def destroyed(widget):
            self._about_dialog = None
        # Need to hold a reference, so the object does not get garbage collected
        self._about_dialog = AboutDialog(self)
        self._about_dialog.connect("destroy", destroyed)
        self._about_dialog.run_nonblocking()
    
    def run_error_dialog(self, first, second):
        """
        Display an error dialog
        
        Positional arguments:
        first -- Primary text of the message
        second -- Secondary text of the message
        """
        print(_("Unable to open PDF file: {}").format(second))
        message = Gtk.MessageDialog(self, (Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT), Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, first)
        message.format_secondary_text(second)
        message.set_title("Error")
        message.connect("response", lambda _,x: message.destroy())
        message.show()
        
    def change_pen_color(self, colorbutton):
        """
        Change the pen to a user defined color.
        
        Positional arguments:
        colorbutton -- The Gtk.ColorButton, that triggered this function
        """
        color = colorbutton.get_rgba()
        red = int(color.red*255)
        green = int(color.green*255)
        blue = int(color.blue*255)
        opacity = int(color.alpha*255)
        
        pen.color = red, green, blue, opacity        
    
    def change_pen_size(self, menuitem, linewidth):
        """
        Change the pen to a user defined line width.
        
        Positional arguments:
        menuitem -- The menu item, that triggered this function
        linewidth -- New line width of the pen
        """
        pen.linewidth = linewidth
        
    def zoom_in(self, menuitem):
        """Magnify document"""
        self.layout.set_zoomlevel(change=0.2)
    
    def zoom_out(self, menuitem):
        """Zoom out"""
        self.layout.set_zoomlevel(change=-0.2)
    
    def zoom_100(self, menuitem):
        """Reset Zoom"""
        self.layout.set_zoomlevel(1)

class OverlayDialog(Gtk.EventBox):
    """
    Display a MessageDialog-like widget, while greying out the underlying widget
    """
    def __init__(self):
        """Constructor"""
        Gtk.EventBox.__init__(self)
        self.last_no_data_seconds = 0
        self.timeout_button_text = _("Disconnect and continue locally")
        self.timeout_label_text = _("No response from the server for the last {} seconds.")
        self.disconnect_button_text = _("Continue locally")
        self.disconnect_label_text = _("The connection to the server has been terminated.")
        
        self.set_valign(Gtk.Align.FILL)
        self.set_halign(Gtk.Align.FILL)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0.4))
        
        main = Gtk.Grid()
        eventbox = Gtk.EventBox()
        whitebox = Gtk.Frame()
        grid = Gtk.Grid()
        self.button = Gtk.Button()
        self.label = Gtk.Label()
        self.icon = Gtk.Image()

        main.set_row_homogeneous(True)
        main.set_column_homogeneous(True)
        eventbox.set_valign(Gtk.Align.CENTER)
        eventbox.set_halign(Gtk.Align.CENTER)
        eventbox.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1,1,1,1))
        whitebox.set_shadow_type(Gtk.ShadowType.OUT)
        grid.set_border_width(5)
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)
        self.button.set_valign(Gtk.Align.END)
        self.button.set_halign(Gtk.Align.END)
        self.label.set_line_wrap(True)
        self.icon.set_from_stock(Gtk.STOCK_DIALOG_WARNING, Gtk.IconSize.DIALOG)
        
        grid.attach(self.icon, left=0, top=0, width=1, height=2)
        grid.attach(self.label, left=1, top=0, width=1, height=1)
        grid.attach(self.button, left=1, top=1, width=1, height=1)
        whitebox.add(grid)
        eventbox.add(whitebox)
        main.attach(eventbox, left=1, top=1, width=1, height=1)
        self.add(main)
        
        self.update()
        GObject.timeout_add_seconds(1, self.update)
        self.show_all()
        
        self.button.connect("clicked", self.disconnect_clicked)
        
    def disconnect_clicked(self, widget):
        """Disconnect from the server and close the OverlayDialog."""
        network.disconnect()
        # Call this via a timeout to let the disconnect_event in network.py fire
        GObject.timeout_add(0, self.destroy)

    def update(self):
        if network.is_connected:
            no_data_seconds = int(time() - network.last_data_received + 0.5)
            if not network.is_stalled:
                # The connection problems were solved automatically
                self.destroy()
                return False
            
            self.last_no_data_seconds = no_data_seconds
            self.label.set_text(self.timeout_label_text.format(no_data_seconds))
            self.button.set_label(self.timeout_button_text)
        else:
            self.label.set_text(self.disconnect_label_text)
            self.button.set_label(self.disconnect_button_text)
        return True
