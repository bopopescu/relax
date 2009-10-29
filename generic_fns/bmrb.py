###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing functions for BMRB support."""

# Python module imports.
from os import F_OK, access

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.exp_info import ExpInfo
from generic_fns import exp_info
from relax_errors import RelaxError, RelaxFileError, RelaxFileOverwriteError, RelaxNoPipeError
from relax_io import get_file_path, mkdir_nofail
from specific_fns.setup import get_specific_fn
from version import version_full


def display(version='3.1'):
    """Display the results in the BMRB NMR-STAR format."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Specific results writing function.
    write_function = get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type, raise_error=False)

    # Write the results.
    write_function(sys.stdout, version=version)


def read(file=None, directory=None, version='3.1'):
    """Read the contents of a BMRB NMR-STAR formatted file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Make sure that the data pipe is empty.
    if not ds[ds.current_pipe].is_empty():
        raise RelaxError("The current data pipe is not empty.")

    # Get the full file path.
    file_path = get_file_path(file_name=file, dir=directory)

    # Fail if the file does not exist.
    if not access(file_path, F_OK):
        raise RelaxFileError(file_path)

    # Specific results reading function.
    read_function = get_specific_fn('bmrb_read', ds[ds.current_pipe].pipe_type)

    # Read the results.
    read_function(file_path, version=version)


def write(file=None, directory=None, version='3.1', force=False):
    """Create a BMRB NMR-STAR formatted file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # The special data pipe name directory.
    if directory == 'pipe_name':
        directory = ds.current_pipe

    # Specific results writing function.
    write_function = get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type)

    # Get the full file path.
    file_path = get_file_path(file, directory)

    # Fail if the file already exists and the force flag is False.
    if access(file_path, F_OK) and not force:
        raise RelaxFileOverwriteError(file_path, 'force flag')

    # Print out.
    print("Opening the file '%s' for writing." % file_path)

    # Create the directories.
    mkdir_nofail(directory, verbosity=0)

    # Add the relax citations.
    for id, key in zip(['relax_ref1', 'relax_ref2'], ['relax 1', 'relax 2']):
        cdp.exp_info.add_citation(cite_id=id, authors=exp_info.CITE[key].authors, doi=exp_info.CITE[key].doi, pubmed_id=exp_info.CITE[key].pubmed_id, full_citation=exp_info.CITE[key].full_citation, title=exp_info.CITE[key].title, status=exp_info.CITE[key].status, type=exp_info.CITE[key].type, journal_abbrev=exp_info.CITE[key].journal_abbrev, journal_full=exp_info.CITE[key].journal_full, volume=exp_info.CITE[key].volume, issue=exp_info.CITE[key].issue, page_first=exp_info.CITE[key].page_first, page_last=exp_info.CITE[key].page_last, year=exp_info.CITE[key].year)

    # Add the relax software package.
    cdp.exp_info.software_setup(name=exp_info.SOFTWARE['relax'].name, version=version_full(), vendor_name=exp_info.SOFTWARE['relax'].authors, url=exp_info.SOFTWARE['relax'].url, cite_ids=['relax_ref1', 'relax_ref2'], tasks=exp_info.SOFTWARE['relax'].tasks)

    # Execute the specific BMRB writing code.
    write_function(file_path, version=version)
