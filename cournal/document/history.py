#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Simon Vetter
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

from cournal.network import network

def reset():
    """Reset undo history."""
    global _undo_list, _redo_list
    deactivate_undo()
    deactivate_redo()
    _undo_list = []
    _redo_list = []
    

def init(menu_undo, menu_redo, tool_undo, tool_redo):
    """
    Initialize the undo history.
    
    Positional arguments:
    menu_undo -- undo widget in the menubar
    menu_redo -- redo widget in the menubar
    tool_undo -- undo widget in the toolbar
    tool_redo -- redo widget in the toolbar
    """
    global _menu_undo, _menu_redo, _tool_redo, _tool_undo, _undo_list, _redo_list
    _menu_undo = menu_undo
    _menu_redo = menu_redo
    _tool_undo = tool_undo
    _tool_redo = tool_redo
    _undo_list = []
    _redo_list = []
    
def undo(menuitem):
    """Undo last command."""
    command = _undo_list.pop()
    add_redo_command(command)
    command.undo()
    if len(_undo_list) == 0:
        deactivate_undo()

def redo(menuitem):
    """Redo undone command."""
    command = _redo_list.pop()
    add_undo_command(command, clear_redo=False)
    command.redo()
    if len(_redo_list) == 0:
        deactivate_redo()

def register_draw_item(item, page):
    """
    Register draw item command in history.
    
    Positional arguments:
    item -- drawn item
    page -- page item was drawn on
    """
    add_undo_command(CommandDrawItem(item, page))

def register_delete_item(item, page):
    """
    Register delete item command in history.
    
    Positional arguments:
    item -- deleted item
    page -- page item was deleted from
    """
    add_undo_command(CommandDeleteItem(item, page))

def add_undo_command(command, clear_redo=True):
    """
    Add command to undo history
    
    Positional arguments:
    command -- command to be registered
    
    Keyword arguments:
    clear_redo -- clear redo history
    """
    global _redo_list
    _undo_list.append(command)
    if len(_undo_list) > 20:
        _undo_list.pop(0)
    if len(_undo_list) == 1:
        activate_undo()
    if clear_redo:
        _redo_list = []
        deactivate_redo()

def add_redo_command(command):
    """
    Add command to redo history
    
    Positional arguments:
    command -- command to be registered
    """
    _redo_list.append(command)
    if len(_redo_list) == 1:
        activate_redo()

def deactivate_undo():
    """Deactivate undo buttons."""
    _menu_undo.set_sensitive(False)
    _tool_undo.set_sensitive(False)

def deactivate_redo():
    """Deactivate redo buttons."""
    _menu_redo.set_sensitive(False)
    _tool_redo.set_sensitive(False)

def activate_undo():
    """Activate undo buttons."""
    _menu_undo.set_sensitive(True)
    _tool_undo.set_sensitive(True)

def activate_redo():
    """Activate redo buttons."""
    _menu_redo.set_sensitive(True)
    _tool_redo.set_sensitive(True)

class CommandDrawItem:
    """Draw item command."""
    def __init__(self, item, page):
        self.item = item
        self.page = page
    
    def undo(self):
        self.page.delete_item(self.item, send_to_network=True, register_in_history=False)

    def redo(self):
        self.page.new_item(self.item, send_to_network=True)

class CommandDeleteItem:
    """Delete item command."""
    def __init__(self, item, page):
        self.item = item
        self.page = page
    
    def undo(self):
        self.page.new_item(self.item, send_to_network=True)

    def redo(self):
        self.page.delete_item(self.item, send_to_network=True, register_in_history=False)
