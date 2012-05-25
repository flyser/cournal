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
    def __init__(self, document, page, number):
        self.document = document
        self.pdf = page
        self.number = number
        self.width, self.height = page.get_size()

        self.strokes = []

class Document():
    def __init__(self, filename):
        self.pdf = Poppler.Document.new_from_file("file://" + os.path.abspath(filename),
                                                  None)
        self.pages = list()
        for i in range(self.pdf.get_n_pages()):
            page = Page(self, self.pdf.get_page(i), i)
            self.pages.append(page)
        print("The document has " + str(len(self.pages)) + " pages")

class MyDrawingArea(Gtk.DrawingArea):
    def __init__(self, page, **args):
        Gtk.DrawingArea.__init__(self, **args)
        
        self.page = page
        self.widget_width = 1
        self.widget_height = 1
        self.backbuffer = None
        self.lastpoint = None

        self.set_double_buffered(False)
        self.set_redraw_on_allocate(False)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
#                       Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        self.connect("draw", self.draw)
        self.connect("size-allocate", self.on_size_allocate)
        self.connect("realize", self.set_cursor)
        self.connect("motion_notify_event", self.motion)
        self.connect("button-press-event", self.press)
        self.connect("button-release-event", self.release)

    def set_cursor(self, widget):
        width, height = 4, 4
        
        s = cairo.ImageSurface(cairo.FORMAT_A1, width, height)
        context = cairo.Context(s)
        context.set_source_rgb(0,0,0)
        context.paint()
        
        cursor_pixbuf = Gdk.pixbuf_get_from_surface(s, 0, 0, width, height)
        cursor = Gdk.Cursor.new_from_pixbuf(Gdk.Display.get_default(),
                                            cursor_pixbuf, width/2, height/2)
        self.get_window().set_cursor(cursor)

    def do_get_request_mode(self):
        return Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH
    
    def do_get_preferred_height_for_width(self, width):
        print("get_preferred_height_for_width(", width, ")")
        page_height = self.page.height
        page_width = self.page.width
        return (width*page_height/page_width, width*page_height/page_width)

    def on_size_allocate(self, widget, alloc):
        print("size_allocate", alloc.width, alloc.height)
        self.set_allocation(alloc)
        self.widget_width = alloc.width
        self.widget_height = alloc.height
    
    def draw(self, widget, context):
        print("draw")
        
        factor = self.widget_width / self.page.width
        
        # Check if the page has already been rendered in the correct size
        if not self.backbuffer or self.backbuffer.get_width() != self.widget_width:
            self.backbuffer = widget.get_window().create_similar_surface(
                    cairo.CONTENT_COLOR, self.widget_width, self.widget_height)
            bb_ctx = cairo.Context(self.backbuffer)
            
            # Fill backbuffer with white:
            bb_ctx.set_source_rgb(1, 1, 1)
            bb_ctx.paint()
            bb_ctx.scale(factor,factor)
            
            # Render PDF
            self.page.pdf.render(bb_ctx)
            
            # Render all strokes again
            bb_ctx.set_antialias(cairo.ANTIALIAS_GRAY)
            bb_ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            bb_ctx.set_source_rgb(0,0,0.4)
            for stroke in self.page.strokes:
                bb_ctx.move_to(stroke[0], stroke[1])
                for i in range(int(len(stroke)/2)-1):
                    bb_ctx.line_to(stroke[2*i+2], stroke[2*i+3])
                bb_ctx.stroke()
        context.set_source_surface(self.backbuffer, 0, 0)
        context.paint()
        
    def press(self, widget, event):
        if event.button != 1:
            return
        #print("Press " + str((event.x,event.y)))
        actualWidth = widget.get_allocation().width
        
        self.lastpoint = [event.x, event.y]
        print(self.page.width, "x", self.page.height)
        self.page.strokes.append([event.x*self.page.width/actualWidth, event.y*self.page.width/actualWidth])
        
    def release(self, widget, event):
        if self.lastpoint is None:
            return
        if event.button != 1:
            return
        #print("Release " + str((event.x,event.y)))
        
        print(self.page.strokes)
        
        self.lastpoint = None
        
    def motion(self, widget, event):
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
        self.page.strokes[-1].extend([event.x*self.page.width/actualWidth, event.y*self.page.width/actualWidth])


class MyLayout(Gtk.Layout):
    def __init__(self, document, **args):
        Gtk.Layout.__init__(self, **args)
        self.document = document
        self.children = []
        self.doc_width = 0
        self.doc_height = 0
        
        for page in self.document.pages:
            self.doc_width = max(self.doc_width, page.width)
            self.doc_height += page.height
            self.children.append(MyDrawingArea(page))
            self.put(self.children[-1], 0, 0)
            
        self.set_double_buffered(False)
        self.set_redraw_on_allocate(False)

        self.connect("draw", self.draw)
     
    def allocate_child(self, child, x, y, width):
        r = Gdk.Rectangle()
        r.x = x
        r.y = y
        r.width = width
        r.height = child.do_get_preferred_height_for_width(width)[0]
        child.size_allocate(r)
        return r.height
           
    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)

        new_width = allocation.width
        new_height = allocation.width*self.doc_height/self.doc_width
        old_width, old_height = self.get_size()
        
        if old_width != new_width:
            print("Ly: size_allocate")
            self.set_size(new_width, new_height)
            y = 0
            for child in self.children:
                y += self.allocate_child(child, 0, y, new_width)
        
        if self.get_realized():
            self.get_window().move_resize(allocation.x, allocation.y,
                                          allocation.width, new_height)
            self.get_bin_window().resize(max(0, allocation.width),
                                         max(0, new_height))
    def draw(self, widget, context):
        print("Ly: draw")

class MyWindow(Gtk.Window):
    def __init__(self, **args):
        Gtk.Window.__init__(self, **args)
        self.set_default_size(width=500, height=200)
        
        # Bob the builder
        builder = Gtk.Builder()
        builder.add_from_file("mainwindow.glade")
        self.add(builder.get_object("outer_box"))
        
        # Give interesting widgets names:
        self.layout = MyLayout(document)
        builder.get_object("scrolledwindow").add(self.layout)
        

        
document = Document(sys.argv[1])

window = MyWindow(title="Cournal")
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
