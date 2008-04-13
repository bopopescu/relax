###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2007 Edward d'Auvergne                             #
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
"""Module for manipulating data pipes."""


# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError, RelaxPipeError

# Relaxation curve fitting modules compilation test.
C_module_exp_fn = 1
try:
    from maths_fns.relax_fit import func
except ImportError:
    C_module_exp_fn = 0


def copy(pipe_from=None, pipe_to=None):
    """Copy the contents of the source data pipe to a new target data pipe.

    If the 'pipe_from' argument is None then the current data pipe is assumed as the source.  The
    data pipe corresponding to 'pipe_to' cannot exist.

    @param pipe_from:   The name of the source data pipe to copy the data from.
    @type pipe_from:    str
    @param pipe_to:     The name of the target data pipe to copy the data to.
    @type pipe_to:      str
    """

    # Test if the pipe already exists.
    if pipe_to in relax_data_store.keys():
        raise RelaxPipeError, pipe_to

    # The current data pipe.
    if pipe_from == None:
        pipe_from = relax_data_store.current_pipe

    # Copy the data.
    relax_data_store[pipe_to] = relax_data_store[pipe_from].__clone__()


def create(pipe_name=None, pipe_type=None):
    """Create a new data pipe.

    The current data pipe will be changed to this new data pipe.


    @param pipe_name:   The name of the new data pipe.
    @type pipe_name:    str
    @param pipe_type:   The new data pipe type which can be one of the following:
        'ct':  Consistency testing,
        'jw':  Reduced spectral density mapping,
        'mf':  Model-free analysis,
        'N-state':  N-state model of domain dynamics,
        'noe':  Steady state NOE calculation,
        'relax_fit':  Relaxation curve fitting,
        'srls':  SRLS analysis.
    @type pipe_type:    str
    """

    # List of valid data pipe types.
    valid = ['ct', 'jw', 'mf', 'N-state', 'noe', 'relax_fit', 'srls']

    # Test if pipe_type is valid.
    if not pipe_type in valid:
        raise RelaxError, "The data pipe type " + `pipe_type` + " is invalid and must be one of the strings in the list " + `valid` + "."

    # Test that the C modules have been loaded.
    if pipe_type == 'relax_fit' and not C_module_exp_fn:
        raise RelaxError, "Relaxation curve fitting is not availible.  Try compiling the C modules on your platform."

    # Add the data pipe.
    relax_data_store.add(pipe_name=pipe_name, pipe_type=pipe_type)


def current():
    """Return the name of the current data pipe.
    
    @return:        The name of the current data pipe.
    @rtype:         str
    """

    return relax_data_store.current_pipe


def delete(pipe_name=None):
    """Delete a data pipe.

    @param pipe_name:   The name of the data pipe to delete.
    @type pipe_name:    str
    """

    # Test if the data pipe exists.
    if pipe_name != None and not relax_data_store.has_key(pipe_name):
        raise RelaxNoPipeError, pipe_name

    # Delete the data pipe.
    del relax_data_store[pipe_name]

    # Set the current data pipe to None if it is the deleted data pipe.
    if relax_data_store.current_pipe == pipe_name:
        relax_data_store.current_pipe = None


def list():
    """Print the details of all the data pipes."""

    # Heading.
    print "%-20s%-20s" % ("Data pipe name", "Data pipe type")

    # Loop over the data pipes.
    for pipe_name in relax_data_store:
        print "%-20s%-20s" % (pipe_name, relax_data_store[pipe_name].pipe_type)


def switch(pipe_name=None):
    """Switch the current data pipe to the given data pipe.

    @param pipe_name:   The name of the data pipe to switch to.
    @type pipe_name:    str
    """

    # Test if the data pipe exists.
    if not relax_data_store.has_key(pipe_name):
        raise RelaxNoPipeError, pipe_name

    # Switch the current data pipe.
    relax_data_store.current_pipe = pipe_name


def test(pipe_name=None):
    """Function for testing the existence of the current or supplied data pipe.

    @param pipe_name:   The name of the data pipe to switch to.
    @type pipe_name:    str
    @return:            The answer to the question of whether the pipe exists.
    @rtype:             Boolean
    """

    # No supplied data pipe and no current data pipe.
    if pipe_name == None:
        # Get the current pipe.
        pipe_name = current()

        # Still no luck.
        if pipe_name == None:
            raise RelaxNoPipeError

    # Test if the data pipe exists.
    if not relax_data_store.has_key(pipe_name):
        raise RelaxNoPipeError, pipe_name

