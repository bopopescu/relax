###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2008 Edward d'Auvergne                             #
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

# Python module imports.
from os import popen
from string import split

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import exists_mol_res_spin_data
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError
from relax_io import open_write_file, test_binary
from specific_fns import get_specific_fn


command_history = ""
"""Variable for storing the Molmol command history."""


def clear_history():
    """Function for clearing the Molmol command history."""

    command_history = ""


def command(command):
    """Function for sending Molmol commands to the program pipe.

    @param command: The Molmol command to send into Molmol.
    @type command:  str
    """

    # Pass the command to Molmol.
    pipe_write(command)


def create_macro(data_type=None, style=None, colour_start=None, colour_end=None, colour_list=None):
    """Function for creating an array of Molmol commands.

    @param data_type:       The data type or parameter name of which to map its values onto the
                            structure.
    @type data_type:        str
    @param style:           The style for the Molmol macro.
    @type style:            str
    @param colour_start:    The starting colour.
    @type colour_start:     str or list of 3 floats
    @param colour_end:      The terminating colour.
    @type colour_end:       str or list of 3 floats
    @param colour_list:     The type of colour being specified (either 'molmol' or 'x11').
    @type colour_list:      str
    @return:                The Molmol macro consisting of a set of Molmol commands.
    @rtype:                 str
    """

    # Specific Molmol macro creation function.
    molmol_macro = get_specific_fn('molmol_macro', relax_data_store[relax_data_store.current_pipe].pipe_type)

    # Get the macro.
    commands = molmol_macro(data_type, style, colour_start, colour_end, colour_list)

    # Return the Molmol commands.
    return commands


def macro_exec(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Function for executing a Molmol macro.

    @param data_type:       The data type or parameter name of which to map its values onto the
                            structure.
    @type data_type:        str
    @param style:           The style for the Molmol macro.
    @type style:            str
    @param colour_start:    The starting colour.
    @type colour_start:     str or list of 3 floats
    @param colour_end:      The terminating colour.
    @type colour_end:       str or list of 3 floats
    @param colour_list:     The type of colour being specified (either 'molmol' or 'x11').
    @type colour_list:      str
    @return:                The Molmol macro consisting of a set of Molmol commands.
    @rtype:                 str
    """

    # Test if the sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Create the macro.
    commands = create_macro()

    # Loop over the commands and execute them.
    for command in commands:
        pipe_write(command)


def open_pdb():
    """Function for opening the PDB file in Molmol."""

    # Test if the pipe is open.
    if not pipe_open_test():
        return

    # Run InitAll to remove everything from molmol.
    pipe_write("InitAll yes")

    # Open the PDB.
    pipe_write("ReadPdb " + relax_data_store[relax_data_store.current_pipe].structure.file_name)


def pipe_open():
    """Function for opening a Molmol pipe."""

    # Test that the Molmol binary exists.
    test_binary('molmol')

    # Alias the data pipe container.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Open and store the Molmol pipe.
    cdp.molmol = popen("molmol -f -", 'w', 0)

    # Execute the command history.
    if len(command_history) > 0:
        pipe_write(command_history, store_command=0)
        return

    # Test if the PDB file has been loaded.
    if hasattr(cdp, 'structure'):
        open_pdb()

    # Run InitAll to remove everything from molmol.
    else:
        pipe_write("InitAll yes")


def pipe_open_test():
    """Function for testing if the Molmol pipe is open.

    @return:    Whether the Molmol pipe is open or not.
    @rtype:     bool
    """

    # Alias the data pipe container.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if a pipe has been opened.
    if not hasattr(cdp, 'molmol'):
        return False

    # Test if the pipe has been broken.
    try:
        cdp.molmol.write('\n')
    except IOError:
        return False

    # The pipe is open.
    return True


def pipe_write(command=None, store_command=1):
    """Function for writing to the Molmol pipe.

    This function is also used to execute a user supplied Molmol command.
    """

    # Reopen the pipe if needed.
    if not pipe_open_test():
        pipe_open()

    # Write the command to the pipe.
    relax_data_store.molmol.write(command + '\n')

    # Place the command in the command history.
    if store_command:
        command_history = command_history + command + "\n"


def ribbon(run=None):
    """Apply the Molmol ribbon style."""

    # Arguments.
    run = run

    # Test if the run exists.
    if not run in relax_data_store.run_names:
        raise RelaxNoPipeError, run

    # Calculate the protons.
    pipe_write("CalcAtom 'H'")
    pipe_write("CalcAtom 'HN'")

    # Calculate the secondary structure.
    pipe_write("CalcSecondary")

    # Execute the ribbon macro.
    pipe_write("XMacStand ribbon.mac")


def tensor_pdb(run=None, file=None):
    """Display the diffusion tensor geometric structure."""

    # Arguments.
    run = run

    # Test if the run exists.
    if not run in relax_data_store.run_names:
        raise RelaxNoPipeError, run

    # To overlay the structure with the diffusion tensor, select all and reorient to the PDB frame.
    pipe_write("SelectAtom ''")
    pipe_write("SelectBond ''")
    pipe_write("SelectAngle ''")
    pipe_write("SelectDist ''")
    pipe_write("SelectPrim ''")
    pipe_write("RotateInit")
    pipe_write("MoveInit")

    # Read in the tensor PDB file and force Molmol to recognise the CONECT records (not that it will show the bonds)!
    pipe_write("ReadPdb " + file)
    file_parts = split(file, '.')
    pipe_write("SelectMol '@" + file_parts[0] + "'")
    pipe_write("CalcBond 1 1 1")

    # Apply the 'ball/stick' style to the tensor.
    pipe_write("SelectAtom '0'")
    pipe_write("SelectBond '0'")
    pipe_write("SelectAtom ':TNS'")
    pipe_write("SelectBond ':TNS'")
    pipe_write("XMacStand ball_stick.mac")

    # Touch up.
    pipe_write("RadiusAtom 1")
    pipe_write("SelectAtom ':TNS@C*'")
    pipe_write("RadiusAtom 1.5")


def view(run=None):
    """Function for running Molmol."""

    # Arguments.
    run = run

    # Open a Molmol pipe.
    if pipe_open_test():
        raise RelaxError, "The Molmol pipe already exists."
    else:
        pipe_open()


def write(run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir=None, force=0):
    """Function for creating a Molmol macro."""

    # Arguments.
    run = run
    data_type = data_type
    style = style
    colour_start = colour_start
    colour_end = colour_end
    colour_list = colour_list

    # Test if the run exists.
    if not run in relax_data_store.run_names:
        raise RelaxNoPipeError, run

    # Test if the sequence data is loaded.
    if not relax_data_store.res.has_key(run):
        raise RelaxNoSequenceError, run

    # Create the macro.
    commands = create_macro()

    # File name.
    if file == None:
        file = data_type + '.mac'

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Loop over the commands and write them.
    for command in commands:
        file.write(command + "\n")

    # Close the file.
    file.close()
