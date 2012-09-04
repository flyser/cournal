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

from cournal.viewer.tools import pen, eraser, navigation

class PageWidget(Gtk.DrawingArea):
    """
    A widget displaying a PDF page and its annotations
    """

    def __init__(self, page, parent, **args):
        """
        Constructor
        
        Positional arguments:
        page -- The Page object to display
        
        Keyword arguments:
        **args -- Arguments passed to the Gtk.DrawingArea constructor
        """

        Gtk.DrawingArea.__init__(self, **args)
        
        self.page = page
        self.parent = parent
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
        """
        Set the cursor to a black square indicating the pen tip
        
        Keyword arguments:
        widget -- The widget to set the cursor for
        """
        width, height = 4, 4
        
        s = cairo.ImageSurface(cairo.FORMAT_A1, width, height)
        context = cairo.Context(s)
        context.set_source_rgb(0,0,0)
        context.paint()
        
        cursor_pixbuf = Gdk.pixbuf_get_from_surface(s, 0, 0, width, height)
        cursor = Gdk.Cursor.new_from_pixbuf(Gdk.Display.get_default(),
                                            cursor_pixbuf, width/2, height/2)
        widget.get_window().set_cursor(cursor)

    def do_get_request_mode(self):
        """Tell Gtk that we like to calculate our height given a width."""
        return Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH
    
    def do_get_preferred_height_for_width(self, width):
        """
        Tell Gtk what height we would like to occupy, if it gives us a width.
        
        Positional arguments:
        width -- width given by Gtk
        """
        aspect_ratio = self.page.width / self.page.height
        return (width / aspect_ratio, width / aspect_ratio)

    def on_size_allocate(self, widget, alloc):
        """
        Called, when the widget was resized.
        
        Positional arguments:
        widget -- The resized widget
        alloc -- A Gtk.Allocation object
        """
        self.set_allocation(alloc)
        self.widget_width = alloc.width
        self.widget_height = alloc.height
    
    def draw(self, widget, context):
        """
        Draw the widget (the PDF, all strokes and the background). Called by Gtk.
        
        Positional arguments:
        widget -- The widget to redraw
        context -- A Cairo context to draw on
        """
        scaling = self.widget_width / self.page.width
        
        # Check if the page has already been rendered in the correct size
        if not self.backbuffer or self.backbuffer.get_width() != self.widget_width or self.backbuffer_valid is False:
            self.backbuffer = cairo.ImageSurface(
                 cairo.FORMAT_ARGB32, self.widget_width, self.widget_height)
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
        """
        Mouse down event. Select a tool depending on the mouse button and call it.
        
        Positional arguments:
        widget -- The widget, which triggered the event
        event -- The Gdk.Event, which stores the location of the pointer
        """
        if event.button == 1:
            self.active_tool = pen
        elif event.button == 2:
            self.active_tool = navigation
        elif event.button == 3:
            self.active_tool = eraser
        else:
            return
        self.active_tool.press(self, event)
    
    def motion(self, widget, event):
        """
        Mouse motion event. Call currently active tool, if any.
        
        Positional arguments: see press()
        """
        if self.active_tool is not None:
            self.active_tool.motion(self, event)
    
    def release(self, widget, event):
        """
        Mouse release event. Call currently active tool, if any.
        
        Positional arguments: see press()
        """
        if self.active_tool is not None:
            self.active_tool.release(self, event)
            self.active_tool = None
    
    def draw_remote_stroke(self, stroke):
        """
        Draw a single stroke on the widget.
        Meant to be called by networking code, when a remote user drew a stroke.
        
        Positional arguments:
        stroke -- The Stroke object, which is to be drawn.
        """
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
            if self.get_window():
                self.get_window().invalidate_rect(update_rect, False)
    
    def delete_remote_stroke(self, stroke):
        """
        Rerender the part of the widget, where a stroke was deleted
        Meant do be called by networking code, when a remote user deleted a stroke.
        
        Positional arguments:
        stroke -- The Stroke object, which was deleted.
        """
        if self.backbuffer:
            self.backbuffer_valid = False
            if self.get_window():
                self.get_window().invalidate_rect(None, False)
