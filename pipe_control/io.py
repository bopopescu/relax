###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the using of pipe_control.io."""

# Python module imports.
import sys

# relax module imports.
from lib.errors import RelaxError
from lib.io import get_file_list
from lib.text.sectioning import section
from pipe_control.pipes import check_pipe


def add_io_data(object_name=None, io_id=None, io_data=None):
    """Add the io data to the data store under the the given object_name within a dictionary with io_id key.

    @keyword object_name:   The object name for where to store the data.  As cdp.object_name.
    @type object_name:      str
    @keyword io_id:         The dictionary key, to access the data.  As As cdp.object_name['io_id']
    @type io_id:            str
    @keyword io_data:       The type of data depending on called function.
    @type io_data:          depend on function
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, object_name):
        setattr(cdp, object_name, {})

    # Add the data under the dictionary key.
    obj_dict = getattr(cdp, object_name)
    obj_dict[io_id] = io_data


def add_io_id(io_id=None):
    """Add the io ID to the data store.

    @keyword io_id:   The io ID string.
    @type io_id:      str
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, 'io_ids'):
        cdp.io_ids = []

    # The ID already exists.
    if io_id in cdp.io_ids:
        return

    # Add the ID.
    cdp.io_ids.append(io_id)


def file_list(glob=None, dir=None, id=None):
    """Store in cdp.io_basename and cdp.io_file_root, a list of file basenames and a list of fileroot matching the pathname pattern.  It is stored in a dictionary with key 'id'.
    If 'id' is set to None, it is stored with the key set to the glob pattern.

    @param glob:            Glob pattern that may contain simple shell-style wildcards.
    @type glob:             str
    @param dir:             The path where the files is located.  If None, then the current directory is assumed.
    @type dir:              str
    @param id:              The id to use as dictionary key, to store the file list.  If None, then the glob pattern is used as id.
    @type id:               None or str
    """

    # Data checks.
    check_pipe()

    # Get the file list.
    basename_list, file_root_list = get_file_list(glob_pattern=glob, dir=dir)

    # Store the results.
    if id == None:
        id = glob

    # Add the io_id to the data store.
    add_io_id(io_id=id)
    # Printout.
    section(file=sys.stdout, text="File list for ID='%s'"%(id), prespace=2)

    # Store in cdp and print info.
    add_io_data(object_name='io_glob', io_id=id, io_data=glob)
    print('cdp.io_glob["%s"] = "%s"'%(id, cdp.io_glob[id]))

    add_io_data(object_name='io_basename', io_id=id, io_data=basename_list)
    print('cdp.io_basename["%s"] = %s'%(id, cdp.io_basename[id]))

    add_io_data(object_name='io_file_root', io_id=id, io_data=file_root_list)
    print('cdp.io_file_root["%s"] = %s'%(id, cdp.io_file_root[id]))

    add_io_data(object_name='io_dir', io_id=id, io_data=dir)
    print('cdp.io_dir["%s"] = "%s"'%(id, cdp.io_dir[id]))