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
    
def init(undo_action, redo_action):
    """
    Initialize the undo history.
    
    Positional arguments:
    undo_action -- Gtk.Action for undo
    redo_action -- Gtk.Action for redo
    """
    global _undo_action, _redo_action, _undo_list, _redo_list
    _undo_action = undo_action
    _redo_action = redo_action
    _undo_list = []
    _redo_list = []
    
def reset():
    """Reset undo history."""
    global _undo_list, _redo_list
    _undo_action.set_sensitive(False)
    _redo_action.set_sensitive(False)
    _undo_list = []
    _redo_list = []

def undo(action):
    """Undo last command."""
    command = _undo_list.pop()
    add_redo_command(command)
    command.undo()
    if len(_undo_list) == 0:
        _undo_action.set_sensitive(False)

def redo(action):
    """Redo undone command."""
    command = _redo_list.pop()
    add_undo_command(command, clear_redo=False)
    command.redo()
    if len(_redo_list) == 0:
        _redo_action.set_sensitive(False)

def register_draw_stroke(stroke, page):
    """
    Register draw stroke command in history.
    
    Positional arguments:
    stroke -- drawn stroke
    page -- page stroke was drawn on
    """
    add_undo_command(CommandDrawStroke(stroke, page))

def register_delete_stroke(stroke, page):
    """
    Register delete stroke command in history.
    
    Positional arguments:
    stroke -- deleted stroke
    page -- page stroke was deleted from
    """
    add_undo_command(CommandDeleteStroke(stroke, page))

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
        _undo_action.set_sensitive(True)
    if clear_redo:
        _redo_list = []
        _redo_action.set_sensitive(False)

def add_redo_command(command):
    """
    Add command to redo history
    
    Positional arguments:
    command -- command to be registered
    """
    _redo_list.append(command)
    if len(_redo_list) == 1:
        _redo_action.set_sensitive(True)

class CommandDrawStroke:
    """Draw stroke command."""
    def __init__(self, stroke, page):
        self.stroke = stroke
        self.page = page
    
    def undo(self):
        self.page.delete_stroke(self.stroke, send_to_network=True, register_in_history=False)

    def redo(self):
        self.page.new_stroke(self.stroke, send_to_network=True)

class CommandDeleteStroke:
    """Delete stroke command."""
    def __init__(self, stroke, page):
        self.stroke = stroke
        self.page = page
    
    def undo(self):
        self.page.new_stroke(self.stroke, send_to_network=True)

    def redo(self):
        self.page.delete_stroke(self.stroke, send_to_network=True, register_in_history=False)
