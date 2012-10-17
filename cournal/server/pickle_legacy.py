#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
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

import os
import json
import pickle
from tempfile import NamedTemporaryFile

import cournal.server as server

def run(from_dir, to_dir=None):
    """
    Convert the pickled documents (cnl-*.save) to the new json file format
    
    Arguments:
    from_dir -- Path of the directory where the old .save files are
    to_dir -- Path of the directory where the new .json files shall be saved to
             (defaults to `from_dir`)
    """
    if to_dir is None:
        to_dir = from_dir

    for filename in [s for s in os.listdir(from_dir) if s.startswith("cnl-") and s.endswith(".save")]:
        if os.path.exists(os.path.join(to_dir, filename[:-5] + ".json")):
            continue
        name = server.server.filename_to_docname(filename)
        with open(os.path.join(from_dir, filename), "rb") as file:
            document = server.server.Document(name)
            document.pages = pickle.load(file)
        _save(document, to_dir)
        print(_(\
"""NOTE:  Found document '{}' saved by cournal-server 0.2.1 or earlier. It will be
       converted to a new file format. Please make sure the conversion went fine and
       delete the old file: '{}'.""").format(name, filename))
        
def _save(document, dir):
    """
    Saves the given Document() in the given directory as a .json file
    
    Arguments:
    document -- The Document instance which shall be saved
    dir -- The path where the file shall be saved to
    """
    # We write to a tmpfile and move it to the actual location to ensure
    # atomic writing of the file, meaning: In case of a crash, either the
    # old or the new version of that file is on the disk
    filename = server.server.docname_to_filename(document.name)
    tmpfile = NamedTemporaryFile(prefix=filename[:-5]+'-', suffix='.delete-me', dir=dir, mode='w', delete=False)
    tmpfile.write(str(server.server.FILE_FORMAT_VERSION) + '\n')
    json.dump(document, tmpfile, cls=server.server.CournalEncoder)
    tmpfile.close()
    os.rename(tmpfile.name, os.path.join(dir, filename))
