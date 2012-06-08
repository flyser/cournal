#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of xoj2tikz.
# Copyright (C) 2012 Fabian Henze
# 
# xoj2tikz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# xoj2tikz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with xoj2tikz.  If not, see <http://www.gnu.org/licenses/>.

import sys
import re
from gzip import open as open_xoj

import xml.etree.cElementTree as ET

from . import Document, Stroke

"""A simplified parser for Xournal files using the ElementTree API."""

def new_document(filename, window):
    with open_xoj(filename, "rb") as input:
        tree = ET.parse(input)
    pdfname = _get_background(tree)
    document = Document(pdfname)

    
    return import_into_document(document, filename, window)

def import_into_document(document, filename, window):
    """
    Parse a Xournal .xoj file (wrapper function of ElementTree.parse())
    
    Note that while .xoj files are gzip-compressed xml files, this function
    expects decompressed input.
    
    Positional Arguments:
    input -- A file-like object or a string with Xournal XML content (NOT gziped)
    """
    with open_xoj(filename, "rb") as input:
        tree = ET.parse(input)
    
    if tree.getroot().tag != "xournal":
        raise Exception("Not a xournal document")

    pages = tree.findall("page")
    for p in range(len(pages)):
        
        # we ignore layers for now. Cournal uses only layer 0
        strokes = pages[p].findall("layer/stroke")
        for s in range(len(strokes)):
            stroke = _parse_stroke(strokes[s], document.pages[p].layers[0])
            document.pages[p].new_stroke(stroke, send_to_network=True)
    return document

def _parse_stroke(stroke, layer):
    """Parse 'stroke' element"""
    
    tool = stroke.attrib["tool"]
    if tool not in ["pen", "eraser", "highlighter"]:
        print("Warning: Unknown tool '{0}' in stroke, ignoring.".format(tool),
              file=sys.stderr)
        return

    coordinates = []
    temp = [float(x) for x in stroke.text.strip().split(' ') if len(x) > 0]
    widths = [max(0.0, float(x)) for x in stroke.attrib["width"].split(' ')]
    nominalWidth = widths.pop(0)
    if tool == "highlighter":
        color = parse_color(stroke.attrib["color"], default_opacity=128)
    else:
        color = parse_color(stroke.attrib["color"])
    
    for i in range(0, len(temp), 2):
        x = temp[i]
        y = temp[i+1]
        if len(widths) > 0:
            width = widths[int(i/2)-1]
            coordinates.append([x, y, width])
        else:
            coordinates.append([x, y])
    
    # If the stroke is just a point, Xournal saves the same coordinates twice
    if len(coordinates) == 2 and coordinates[0] == coordinates[1]:
        del coordinates[1]

    return Stroke(layer, color=color, linewidth=nominalWidth, coords=coordinates)

def _get_background(tree):
    """Gets the background pdf file name of a xournal document"""
    for bg in tree.findall("page/background"):
        if "filename" in bg.attrib:
            return bg.attrib["filename"]

def parse_color(code, default_opacity=255):
    """
    Parse a xournal color name and return a tuple of four: (r, g, b, opacity)

    Keyword arguments:
    code -- The color string to parse (mandatory)
    default_opacity -- If 'code' does not contain opacity information, use this.
                       (default 255)
    """
    opacity = default_opacity
    regex = re.compile(r"#([0-9a-fA-F]{2})([0-9a-fA-F]{2})"
                       r"([0-9a-fA-F]{2})([0-9a-fA-F]{2})")
    
    if code == "black":
        r, g, b = (0, 0, 0)
    elif code == "blue":
        r, g, b = (51, 51, 204)
    elif code == "red":
        r, g, b = (255, 0, 0)
    elif code == "green":
        r, g, b = (0, 128, 0)
    elif code == "gray":
        r, g, b = (128, 128, 128)
    elif code == "lightblue":
        r, g, b = (0, 192, 255)
    elif code == "lightgreen":
        r, g, b = (0, 255, 0)
    elif code == "magenta":
        r, g, b = (255, 0, 255)
    elif code == "orange":
        r, g, b = (255, 128, 0)
    elif code == "yellow":
        r, g, b = (255, 255, 0)
    elif code == "white":
        r, g, b = (255, 255, 255)
    elif re.match(regex, code):
        r, g, b, opacity = re.match(regex, code).groups()
        r = int(r, 16)
        g = int(g, 16)
        b = int(b, 16)
        opacity = int(opacity, 16)
    else:
        raise Exception("invalid color")
    return (r, g, b, opacity)

# For testing purposes:
if __name__ == "__main__":
    import sys
    f = open_xoj(sys.argv[1], "rb")
    parse(None, None, f)
