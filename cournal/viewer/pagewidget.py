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
import cairo

from .tools import pen, eraser

class PageWidget(Gtk.DrawingArea):
    def __init__(self, page, **args):
        Gtk.DrawingArea.__init__(self, **args)
        
        self.page = page
        page.widget = self        
        self.widget_width = 1
        self.widget_height = 1
        self.backbuffer = None
        self.backbuffer_valid = True
        self.active_tool = None

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)
#                       Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        self.connect("realize", self.set_cursor)
        self.connect("size-allocate", self.on_size_allocate)
        self.connect("draw", self.draw)
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
        #print("get_preferred_height_for_width(", width, ")")
        aspect_ratio = self.page.width / self.page.height
        return (width / aspect_ratio, width / aspect_ratio)

    def on_size_allocate(self, widget, alloc):
        #print("size_allocate", alloc.width, alloc.height)
        self.set_allocation(alloc)
        self.widget_width = alloc.width
        self.widget_height = alloc.height
    
    def draw(self, widget, context):
        #print("draw")
        
        scaling = self.widget_width / self.page.width
        
        # Check if the page has already been rendered in the correct size
        if not self.backbuffer or self.backbuffer.get_width() != self.widget_width or self.backbuffer_valid is False:
            self.backbuffer = widget.get_window().create_similar_surface(
                    cairo.CONTENT_COLOR_ALPHA, self.widget_width, self.widget_height)
            self.backbuffer_valid = True
            bb_ctx = cairo.Context(self.backbuffer)
            
            # For correct rendering of PDF, the PDF is first rendered to a
            # transparent image (all alpha = 0).
            bb_ctx.scale(scaling, scaling)
            bb_ctx.save()
            self.page.pdf.render(bb_ctx)
            bb_ctx.restore()
            
            for stroke in self.page.layers[0].strokes:
                stroke.draw(bb_ctx, scaling)
            
            # Then the image is painted on top of a white "page". Instead of
            # creating a second image, painting it white, then painting the
            # PDF image over it we can use the cairo.OPERATOR_DEST_OVER
            # operator to achieve the same effect with the one image.
            bb_ctx.set_operator(cairo.OPERATOR_DEST_OVER)
            bb_ctx.set_source_rgb(1, 1, 1)
            bb_ctx.paint()
        
        context.set_source_surface(self.backbuffer, 0, 0)
        context.paint()
        
    def press(self, widget, event):
        #print("Press " + str((event.x,event.y)))
        if event.button == 1:
            self.active_tool = pen
        elif event.button == 3 or event.button == 2:
            self.active_tool = eraser
        else:
            return
        self.active_tool.press(self, event)
    
    def motion(self, widget, event):
        #print("\rMotion "+str((event.x,event.y))+"  ", end="")
        if self.active_tool is not None:
            self.active_tool.motion(self, event)
    
    def release(self, widget, event):
        if self.active_tool is not None:
            self.active_tool.release(self, event)
            self.active_tool = None
    
    def draw_remote_stroke(self, stroke):
        if self.backbuffer:
            scaling = self.widget_width / self.page.width
            context = cairo.Context(self.backbuffer)
            
            context.scale(scaling, scaling)
            x, y, x2, y2 = stroke.draw(context, scaling)
            
            update_rect = Gdk.Rectangle()
            update_rect.x = x-2
            update_rect.y = y-2
            update_rect.width = x2-x+4
            update_rect.height = y2-y+4
            self.get_window().invalidate_rect(update_rect, False)
    
    def delete_remote_stroke(self, stroke):
        if self.backbuffer:
            self.backbuffer_valid = False
            self.get_window().invalidate_rect(None, False)
