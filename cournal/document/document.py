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

import os
import gzip

from gi.repository import Poppler
import cairo

from . import Page

class Document:
    def __init__(self, pdfname):
        self.pdfname = os.path.abspath(pdfname)
        self.pdf = Poppler.Document.new_from_file("file://" + self.pdfname, None)
        self.width = 0
        self.height = 0
        self.pages = []
        
        for i in range(self.pdf.get_n_pages()):
            page = Page(self, self.pdf.get_page(i), i)
            self.pages.append(page)
            
            self.width = max(self.width, page.width)
            self.height += page.height

        print("The document has " + str(len(self.pages)) + " pages")
        
    def clear_pages(self):
        for page in self.pages:
            for stroke in page.layers[0].strokes[:]:
                page.delete_stroke_callback(stroke)
        
    def export_pdf(self, filename):
        try:
            surface = cairo.PDFSurface(filename, 0, 0)
        except IOError as ex:
            print("Error saving document:", ex)
            #FIXME: Move error handler to mainwindow.py and show error message
            return
        
        for page in self.pages:
            surface.set_size(page.width, page.height)
            context = cairo.Context(surface)
            
            page.pdf.render_for_printing(context)
            
            # Render all strokes
            context.set_source_rgb(0,0,0.4)
            context.set_antialias(cairo.ANTIALIAS_GRAY)
            context.set_line_cap(cairo.LINE_CAP_ROUND)
            context.set_line_join(cairo.LINE_JOIN_ROUND)
            context.set_line_width(1.5)

            for stroke in page.layers[0].strokes:
                first = stroke.coords[0]
                
                context.move_to(first[0], first[1])
                if len(stroke.coords) > 1:
                    for coord in stroke.coords:
                        context.line_to(coord[0], coord[1])
                else:
                    context.line_to(first[0], first[1])
                context.stroke()
            
            surface.show_page() # aka "next page"

    def save_xoj_file(self, filename):
        pagenum = 1
        try:
            f = gzip.open(filename, "wb")
        except IOError as ex:
            print("Error saving document:", ex)
            #FIXME: Move error handler to mainwindow.py and show error message
            return
        
        # Thanks to Xournals awesome XML(-not)-parsing, we cant use elementtree here.
        # In "Xournal World", <t a="a" b="b"> is not the same as <t b="b" a="a"> ...
        
        r = "<?xml version=\"1.0\" standalone=\"no\"?>\n"
        r += "<xournal version=\"0.4.6\">\n"
        r += "<title>Xournal document - see http://math.mit.edu/~auroux/software/xournal/</title>\n"
        
        for page in self.pages:
            r += "<page width=\"" + str(round(page.width, 2)) + "\" height=\"" + str(round(page.height, 2)) + "\">\n"
            r += "<background type=\"pdf\""
            if pagenum == 1:
                r += " domain=\"absolute\" filename=\"" + self.pdfname + "\""
            r += " pageno=\"" + str(pagenum) + "\" />\n"
            pagenum += 1
            
            for layer in page.layers:
                r += "<layer>\n"
                for stroke in layer.strokes:
                    r += "<stroke tool=\"pen\" color=\"#000066FF\" width=\"1.41\">\n"
                    for coord in stroke.coords:
                        r += " {} {}".format(coord[0], coord[1])
                    if len(stroke.coords) < 2:
                        r += " {} {}".format(stroke.coord[0][0], stroke.coords[0][1])
                    r += "\n</stroke>\n"
                r += "</layer>\n"
                r += "</page>\n"
        r += "</xournal>"
        
        f.write(bytes(r, "UTF-8"))
        f.close()
