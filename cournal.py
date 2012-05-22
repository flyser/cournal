#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Cournal: A collaborative note taking and journal application with a stylus.
# Copyright (C) 2012 Fabian Henze
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os

from twisted.internet import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

from gi.repository import Gtk, Poppler, Gdk
import cairo

class Page():
    def __init__(self, page):
        self.pdf = page
        self.width, self.height = page.get_size()

        self.strokes = list()

class Document():
    def __init__(self, filename):
        self.pdf = Poppler.Document.new_from_file("file://" + os.path.abspath(filename),
                                                  None)
        self.pages = list()
        for i in range(self.pdf.get_n_pages()):
            page = Page(self.pdf.get_page(i))
            self.pages.append(page)
        print("The document has " + str(len(self.pages)) + " pages")

class MyWindow(Gtk.Window):
    def __init__(self, **args):
        Gtk.Window.__init__(self, **args)
        self.set_default_size(width=700, height=800)
        
        self.backbuffer = None
        self.lastpoint = None

        # Bob the builder
        builder = Gtk.Builder()
        builder.add_from_file("mainwindow.glade")
        self.add(builder.get_object("outer_box"))
        
        # Give interesting widgets names:
        self.viewport = builder.get_object("viewport")
        self.drawingarea = builder.get_object("drawingarea")
        
        # Initialize the drawing area:
        self.drawingarea.set_double_buffered(False)
        self.drawingarea.set_size_request(width=100, height=800)
        self.drawingarea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                                    Gdk.EventMask.BUTTON_RELEASE_MASK |
                                    Gdk.EventMask.POINTER_MOTION_MASK)
#                                    Gdk.EventMask.POINTER_MOTION_HINT_MASK)
        
        self.drawingarea.connect("draw", self.draw_drawingarea)
        self.drawingarea.connect("configure_event", self.configure_drawingarea)
        self.drawingarea.connect("motion_notify_event", self.motion_drawingarea)
        self.drawingarea.connect("button-press-event", self.press_drawingarea)
        self.drawingarea.connect("button-release-event", self.release_drawingarea)
        
    def set_cursor(self):
        width, height = 4, 4
        
        s = cairo.ImageSurface(cairo.FORMAT_A1, width, height)
        context = cairo.Context(s)
        context.set_source_rgb(0,0,0)
        context.paint()
        
        cursor_pixbuf = Gdk.pixbuf_get_from_surface(s, 0, 0, width, height)
        cursor = Gdk.Cursor.new_from_pixbuf(Gdk.Display.get_default(),
                                            cursor_pixbuf, width/2, height/2)
        self.drawingarea.get_window().set_cursor(cursor)
        
    def press_drawingarea(self, widget, event):
        if event.button != 1:
            return
        #print("Press " + str((event.x,event.y)))
        actualWidth = widget.get_allocation().width
        
        self.lastpoint = [event.x, event.y]
        print(currentPage.width, "x", currentPage.height)
        currentPage.strokes.append([event.x*currentPage.width/actualWidth, event.y*currentPage.width/actualWidth])
        
    def release_drawingarea(self, widget, event):
        if self.lastpoint is None:
            return
        if event.button != 1:
            return
        #print("Release " + str((event.x,event.y)))
        
        print(currentPage.strokes)
        
        self.lastpoint = None
        
    def motion_drawingarea(self, widget, event):
        if self.lastpoint is None:
            return
        #print("\rMotion "+str((event.x,event.y))+"  ", end="")
        actualWidth = widget.get_allocation().width
        
        context = cairo.Context(self.backbuffer)
        #context.set_line_width(80)
        context.set_antialias(cairo.ANTIALIAS_GRAY)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.move_to(self.lastpoint[0], self.lastpoint[1])
        
        context.set_source_rgb(0,0,0.4)
        context.line_to(event.x, event.y)
        x, y, x2, y2 = context.stroke_extents()
        context.stroke()
        
        update_rect = Gdk.Rectangle()
        update_rect.x = x-2
        update_rect.y = y-2
        update_rect.width = x2-x+4
        update_rect.height = y2-y+4
        widget.get_window().invalidate_rect(update_rect, False)

        self.lastpoint = [event.x, event.y]
        currentPage.strokes[-1].extend([event.x*currentPage.width/actualWidth, event.y*currentPage.width/actualWidth])
        
    def configure_drawingarea(self, widget, event):
        #print("Configure " + str((event.width, event.height)))
        actualWidth = widget.get_allocation().width
        actualHeight = widget.get_allocation().height
        factor = actualWidth / currentPage.width
        self.backbuffer = widget.get_window().create_similar_surface(cairo.CONTENT_COLOR,
                                                                     actualWidth,
                                                                     currentPage.height*factor)
        context = cairo.Context(self.backbuffer)

        # Fill buffer with white
        context.set_source_rgb(1,1,1)
        context.paint()
        context.scale(factor,factor)
        # Render PDF
        currentPage.pdf.render(context)
        
        # Render all strokes again
        context.set_antialias(cairo.ANTIALIAS_GRAY)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_source_rgb(0,0,0.4)
        for stroke in currentPage.strokes:
            context.move_to(stroke[0], stroke[1])
            for i in range(int(len(stroke)/2)-1):
                context.line_to(stroke[2*i+2], stroke[2*i+3])
            context.stroke()
        
    def draw_drawingarea(self, widget, context):
        #print("Draw")
        # you can ignore the width=100 here. it has no effect
        self.drawingarea.set_size_request(width=100, height=self.backbuffer.get_height())
        self.drawingareaContext = context
        
        context.set_source_surface(self.backbuffer, 0, 0)
        context.paint()


document = Document(sys.argv[1])
currentPage = document.pages[0]

window = MyWindow(title="Cournal")
window.connect("delete-event", Gtk.main_quit)
window.show_all()
window.set_cursor()
Gtk.main()
