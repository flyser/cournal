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
    def __init__(self, filename):
        self.filename = os.path.abspath(filename)
        self.pdf = Poppler.Document.new_from_file("file://" + self.filename, None)
        self.width = 0
        self.height = 0
        self.pages = []
        
        for i in range(self.pdf.get_n_pages()):
            page = Page(self, self.pdf.get_page(i), i)
            self.pages.append(page)
            
            self.width = max(self.width, page.width)
            self.height += page.height

        print("The document has " + str(len(self.pages)) + " pages")
        
    def export_pdf(self, filename):
        surface = cairo.PDFSurface(filename, 0, 0)
        
        for page in self.pages:
            surface.set_size(page.width, page.height)
            context = cairo.Context(surface)
            
            # Fill backbuffer with white:
            context.set_source_rgb(1, 1, 1)
            context.paint()
            
            # Render PDF
            page.pdf.render(context)
            
            # Render all strokes again
            context.set_antialias(cairo.ANTIALIAS_GRAY)
            context.set_line_cap(cairo.LINE_CAP_ROUND)
            context.set_source_rgb(0,0,0.4)
            for stroke in page.strokes:
                context.move_to(stroke[0], stroke[1])
                for i in range(int(len(stroke)/2)-1):
                    context.line_to(stroke[2*i+2], stroke[2*i+3])
                context.stroke()
            surface.show_page() # aka "next page"

    def save_xoj_file(self, filename):
        pagenum = 1
        f = gzip.open(filename, "wb")
        
        # Thanks to Xournals awesome XML(-not)-parsing, we cant use elementtree here.
        # <t a="a" b="b"> is not the same as <t b="b" a="a"> ...
        
        r = "<?xml version=\"1.0\" standalone=\"no\"?>\n"
        r += "<xournal version=\"0.4.5\">\n"
        #r += "<!-- Created with Cournal -->\n"
        r += "<title>Xournal document - see http://math.mit.edu/~auroux/software/xournal/</title>\n"
        
        for p in self.pages:
            r += "<page width=\"" + str(round(p.width, 2)) + "\" height=\"" + str(round(p.height, 2)) + "\">\n"
            r += "<background type=\"pdf\""
            if pagenum == 1:
                r += " domain=\"absolute\" filename=\"" + self.filename + "\""
            r += " pageno=\"" + str(pagenum) + "\" />\n"
            pagenum += 1
            
            r += "<layer>\n"
            for s in p.strokes:
                r += "<stroke tool=\"pen\" color=\"#000066FF\" width=\"1.41\">\n"
                for coord in s:
                    r += " " + str(round(coord, 2))
                if len(s) < 4:
                    r += " " + str(s[0]) + " " + str(s[1])
                r += "\n</stroke>\n"
            r += "</layer>\n"
            r += "</page>\n"
        r += "</xournal>"
        
        f.write(bytes(r, "UTF-8"))
        f.close()
