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

import xml.etree.cElementTree as ET

from . import Page, Layer, Stroke, TextBox

"""A parser for Xournal files using the ElementTree API."""

def parse(file):
    """
    Parse a Xournal .xoj file (wrapper function of ElementTree.parse())
    
    Note that while .xoj files are gzip-compressed xml files, this function
    expects decompressed input.
    
    Positional Arguments:
    file -- A file-like object or a string with Xournal XML content (NOT gziped)
    """
    tree = ET.parse(file)

    if tree.getroot().tag != "xournal":
        raise Exception("Not a xournal document")
    
    return _root(tree.getroot())
    
def _root(root):
    """Parse root element and its subtree"""
    
    pages = []
    
    for element in root:
        if element.tag == "page":
            pages.append(_page(element))
            
        elif element.tag == "title":
            # The title is the same for every Xournal file -> ignore
            pass
        elif element.tag == "preview":
            # previews are base64-encoded png (?) files -> ignore
            pass
        else:
            raise Exception("Unknown tag: xournal/" + element.tag)
        
    return pages

def _page(page):
    """Parse 'page' element and its subtree"""
    
    layers = []
    width = float(page.attrib["width"])
    height = float(page.attrib["height"])
    
    for element in page:
        if element.tag == "layer":
            layers.append(_layer(element))
        
        elif element.tag == "background":
            pass #TODO
        else:
            raise Exception("Unknown tag: xournal/page/" + element.tag)
    
    return Page(layerList=layers, width=width, height=height)

def _layer(layer):
    """Parse 'layer' element and its subtree"""
    
    items = []
    item = None
    
    for element in layer:
        if element.tag == "stroke":
            item = _stroke(element)
        elif element.tag == "text":
            item = _text(element)
        
        elif element.tag == "image":
            pass #TODO
        else:
            raise Exception("Unknown tag: xournal/page/layer/" + element.tag)
        
        if item is not None:
            items.append(item)
    
    return Layer(itemList=items)

def _stroke(stroke):
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
        color = getColor(stroke.attrib["color"], defaultOpacity=128)
    else:
        color = getColor(stroke.attrib["color"])
    
    for i in range(0, len(temp), 2):
        x = temp[i]
        y = temp[i+1]
        if len(widths) > 0:
            width = widths[int(i/2)-1]
            coordinates.append([x, y, width])
        else:
            coordinates.append([x, y])

    return Stroke(color=color, coordList=coordinates, width=nominalWidth)
    
def _text(text):
    """Parse 'text' element"""
    
    font = text.attrib["font"]
    size = float(text.attrib["size"])
    x = float(text.attrib["x"])
    y = float(text.attrib["y"])
    color = getColor(text.attrib["color"])
    content = text.text
    
    return TextBox(font=font, size=size, x=x, y=y, color=color, text=content)

def getColor(code, defaultOpacity=1.0):
    """
    Parse a xournal color name and return a tuple of four: (r, g, b, opacity)

    Keyword arguments:
    code -- The color string to parse (mandatory)
    defaultOpacity -- If 'code' does not contain opacity information, use this.
                      (default 255)
    """
    opacity = defaultOpacity
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
