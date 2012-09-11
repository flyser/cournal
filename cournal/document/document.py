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

from os.path import abspath
from gzip import open as open_xoj

from gi.repository import Poppler, GLib
import cairo

from cournal.document.page import Page
from cournal.document import history
from cournal.document import search

class Document:
    """
    A Cournal document, having multiple pages.
    """
    def __init__(self, pdfname):
        """
        Constructor
        
        Positional arguments:
        pdfname -- The filename of the PDF document, which will be annotated
        """

        self.pdfname = abspath(pdfname)
        uri = GLib.filename_to_uri(self.pdfname, None)
        self.pdf = Poppler.Document.new_from_file(uri, None)
        search.set_pdf(self.pdf)
        self.width = 0
        self.height = 0
        self.pages = []
        history.reset()
                
        for i in range(self.pdf.get_n_pages()):
            page = Page(self, self.pdf.get_page(i), i)
            self.pages.append(page)
            
            self.width = max(self.width, page.width)
            self.height += page.height
            self.num_of_pages = len(self.pages)
        
        print(_("The document has {} pages").format(self.num_of_pages))
        
    def is_empty(self):
        """
        Returns True, if no page of this document has a stroke on it.
        Otherwise False
        """
        for page in self.pages:
            if len(page.layers[0].strokes) != 0:
                return False
        return True

    def clear_pages(self):
        """Deletes all strokes on all pages of this document"""
        for page in self.pages:
            for stroke in page.layers[0].strokes[:]:
                page.delete_stroke(stroke, send_to_network=False)
    
    def export_pdf(self, filename):
        """
        Save the whole document (PDF+annotations) as a PDF file.
        
        Positional arguments:
        filename -- filename of the new PDF file.
        """
        try:
            surface = cairo.PDFSurface(filename, 0, 0)
        except IOError as ex:
            print(_("Error saving document: {}").format(ex))
            #FIXME: Move error handler to mainwindow.py and show error message
            return
        
        for page in self.pages:
            surface.set_size(page.width, page.height)
            context = cairo.Context(surface)
            
            page.pdf.render_for_printing(context)
            
            for stroke in page.layers[0].strokes:
                stroke.draw(context)
            
            surface.show_page() # aka "next page"

    def save_xoj_file(self, filename):
        """
        Save the whole document as a .xoj file.
        
        Positional arguments:
        filename -- filename of the new .xoj file
        """
        pagenum = 1
        try:
            f = open_xoj(filename, "wb")
        except IOError as ex:
            print(_("Error saving document: {}").format(ex))
            #FIXME: Move error handler to mainwindow.py and show error message
            return
        
        # Thanks to Xournals awesome XML(-not)-parsing, we can't use elementtree here.
        # In "Xournal World", <t a="a" b="b"> is not the same as <t b="b" a="a"> ...
        
        r = "<?xml version=\"1.0\" standalone=\"no\"?>\n"
        r += "<xournal version=\"0.4.6\">\n"
        r += "<title>Xournal document - see http://math.mit.edu/~auroux/software/xournal/</title>\n"
        
        for page in self.pages:
            r += "<page width=\"{}\" height=\"{}\">\n".format(round(page.width, 2), round(page.height, 2))
            r += "<background type=\"pdf\""
            if pagenum == 1:
                r += " domain=\"absolute\" filename=\"{}\"".format(self.pdfname)
            r += " pageno=\"{}\" />\n".format(pagenum)
            pagenum += 1
            
            for layer in page.layers:
                r += "<layer>\n"
                for stroke in layer.strokes:
                    red, g, b, opacity = stroke.color
                    r += "<stroke tool=\"pen\" color=\"#{:02X}{:02X}{:02X}{:02X}\" width=\"{}\">\n".format(red, g, b, opacity, stroke.linewidth)
                    first = stroke.coords[0]
                    for coord in stroke.coords:
                        r += " {} {}".format(coord[0], coord[1])
                    if len(stroke.coords) < 2:
                        r += " {} {}".format(first[0], first[1])
                    r += "\n</stroke>\n"
                r += "</layer>\n"
                r += "</page>\n"
        r += "</xournal>"
        
        f.write(bytes(r, "UTF-8"))
        f.close()
